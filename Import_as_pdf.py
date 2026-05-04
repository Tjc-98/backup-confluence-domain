import requests
import sys
import os
import pdfkit

class PDFDownloader:
    def __init__(self, page_id, page_title, base_url, email, token):
        self.page_id = page_id
        self.page_title = page_title
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.token = token

    def _sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        keep_chars = (' ', '.', '_', '-')
        return "".join(c for c in filename if c.isalnum() or c in keep_chars).strip()

    def export_page_as_pdf(self):
        url = f"{self.base_url}/rest/api/content/{self.page_id}?expand=body.view"
        auth = (self.email, self.token)
        headers = {"Accept": "application/json"}
        response = requests.get(url, auth=auth, headers=headers)
        if response.status_code == 200:
            html = response.json()['body']['view']['value']
            print(f"Fetched response {response.content}")
            # print(f"Fetched HTML content for page ID {html}")
            os.makedirs('pdf_exports', exist_ok=True)
            safe_title = self._sanitize_filename(self.page_title)
            output_pdf = f'pdf_exports/{safe_title}_{self.page_id}.pdf'
            try:
                pdfkit.from_string(html, output_pdf)
                print(f"Saved PDF to {output_pdf}")
                return True
            except Exception as e:
                print(f"Failed to convert HTML to PDF: {e}")
                return False
        else:
            print(f"Failed to fetch page: {response.status_code}")
            return False

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python download_pdf.py <PAGE_ID> <PAGE_TITLE> <BASE_URL> <EMAIL> <TOKEN>")
        sys.exit(1)

    downloader = PDFDownloader(
        page_id=sys.argv[1],
        page_title=sys.argv[2],
        base_url=sys.argv[3],
        email=sys.argv[4],
        token=sys.argv[5]
    )
    downloader.export_page_as_pdf()