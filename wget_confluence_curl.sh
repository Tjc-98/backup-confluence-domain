#!/bin/bash

# Load configuration
source "confluence_config.cfg"

BASE_URL="https://$HOSTNAME.atlassian.net/wiki"

# 1. Fetch spaces and save to spaces.json
curl -u "$EMAIL:$TOKEN" \
     -H "User-Agent: Mozilla/5.0" \
     -H "Accept: application/json" \
     "$BASE_URL/rest/api/space?limit=100" \
     -o spaces.json

# Check if file was created
if [ ! -f "spaces.json" ]; then
    echo "ERROR: Failed to create spaces.json"
    exit 1
fi

# Extract non-global space keys using grep/awk
space_keys=($(grep -Po '"key":\s*"\K[^"]+' spaces.json | paste -sd ' '))

# Verify extraction
if [ ${#space_keys[@]} -eq 0 ]; then
    echo "WARNING: No non-global space keys found"
else
    echo "Found ${#space_keys[@]} non-global spaces:"
    printf "  %s\n" "${space_keys[@]}"
fi

# 3. Saving Pages info in pages_$SPACE_KEY
for space_key in "${space_keys[@]}"; do
    echo "Processing space: $space_key"
    curl -u "$EMAIL:$TOKEN" \
        "$BASE_URL/rest/api/content?spaceKey=$space_key" \
        -o "pages_$space_key.json"

    # Extract page IDs and titles using grep/sed/awk
    grep -o '{[^}]*"id":[^}]*"title":[^}]*}' "pages_$space_key.json" | while read -r line; do
        
        PDF_PAGE_ID=$(echo "$line" | grep -o '"id":"[^"]*"' | head -1 | cut -d':' -f2 | tr -d '"')
        PDF_PAGE_TITLE=$(echo "$line" | grep -o '"title":"[^"]*"' | head -1 | cut -d':' -f2- | tr -d '"' | sed 's/[\/:*?"<>|]/_/g')
        SPACE_KEY=$space_key
        
        if [[ -n "$PDF_PAGE_ID" && -n "$PDF_PAGE_TITLE" ]]; then
            echo "  Downloading PDF for page: $PDF_PAGE_TITLE (ID: $PDF_PAGE_ID)"

            python3 download_pdf.py "$PDF_PAGE_ID" "$PDF_PAGE_TITLE" "$BASE_URL" "$EMAIL" "$TOKEN"
            if [ $? -ne 0 ]; then
                echo "ERROR: Failed to generate HTML for page ID $PDF_PAGE_ID"
            else
                HTML_FILE="html_exports/${PDF_PAGE_TITLE}_${PDF_PAGE_ID}.html"
                if [ -f "$HTML_FILE" ]; then
                    python3 html_to_pdf.py "$HTML_FILE"
                    if [ $? -ne 0 ]; then
                        echo "ERROR: Failed to generate PDF for page ID $PDF_PAGE_ID"
                    else
                        echo "  Successfully generated PDF for page: $PDF_PAGE_TITLE"
                    fi
                else
                    echo "ERROR: HTML file not found for page ID $PDF_PAGE_ID, skipping PDF generation."
                fi
            fi
        fi
    done
done


