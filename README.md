# backup-confluence-domain

Downloads Confluence pages and converts them to PDF files using Python and Bash.

---

## About

Written in Python and Bash, this project provides three approaches for exporting Confluence pages as PDF files via the Confluence REST API. It authenticates using an email and API token.

- `wget_confluence_curl.sh` - fetches all spaces and pages in a Confluence instance and orchestrates the full download pipeline via curl and Python scripts.
- `download_pdf.py` - downloads a single Confluence page as HTML, including all linked resources (images, CSS, JS), saving them locally with updated relative paths.
- `html_to_pdf.py` - converts a downloaded HTML file to a PDF using ReportLab, including text content and embedded images.
- `Import_as_pdf.py` - alternative single-page exporter that converts Confluence HTML directly to PDF using `pdfkit` (requires `wkhtmltopdf`).

## Usage

### Full bulk export (shell script)

1. Create a `confluence_config.cfg` file in the project root:
   ```
   HOSTNAME=your-domain
   EMAIL=your@email.com
   TOKEN=your_api_token
   ```
2. Run the shell script:
   ```bash
   bash wget_confluence_curl.sh
   ```
   This fetches all spaces, lists their pages, downloads each page as HTML, and converts each to PDF. Output files are written to `html_exports/` and `pdf_exports/`.

### Single page export

```bash
python3 download_pdf.py <PAGE_ID> <PAGE_TITLE> <BASE_URL> <EMAIL> <TOKEN>
python3 html_to_pdf.py html_exports/<PAGE_TITLE>_<PAGE_ID>.html
```

### Alternative single page export (pdfkit)

```bash
python3 Import_as_pdf.py <PAGE_ID> <PAGE_TITLE> <BASE_URL> <EMAIL> <TOKEN>
```

## Getting Started

### Prerequisites

- Python 3.8 or later
- `requests`, `beautifulsoup4`, `reportlab` (auto-installed by `download_pdf.py` if missing)
- `pdfkit` and `wkhtmltopdf` (required only for `Import_as_pdf.py`)
- Bash (for `wget_confluence_curl.sh`)
- A Confluence API token

### Installing dependencies manually

```bash
pip install requests beautifulsoup4 reportlab pdfkit
```

## Configuration

| Variable | File | Description |
|----------|------|-------------|
| `HOSTNAME` | `confluence_config.cfg` | Your Atlassian subdomain (e.g. `mycompany`) |
| `EMAIL` | `confluence_config.cfg` | Your Atlassian account email |
| `TOKEN` | `confluence_config.cfg` | Your Confluence API token |

---

MIT License - see [LICENSE](LICENSE)
