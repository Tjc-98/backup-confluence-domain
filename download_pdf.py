import sys
import subprocess
import importlib

# Ensure required packages are installed
required = ["requests", "bs4"]
for pkg in required:
    try:
        importlib.import_module(pkg)
    except ImportError:
        print(f"Package '{pkg}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import requests
import os
from bs4 import BeautifulSoup

class HTMLDownloader:
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

    def save_page_with_resources(self):
        url = f"{self.base_url}/rest/api/content/{self.page_id}?expand=body.view"
        auth = (self.email, self.token)
        headers = {"Accept": "application/json"}
        response = requests.get(url, auth=auth, headers=headers)
        if response.status_code == 200:
            html = response.json()['body']['view']['value']
            os.makedirs('html_exports', exist_ok=True)
            safe_title = self._sanitize_filename(self.page_title)
            output_html = f'html_exports/{safe_title}_{self.page_id}.html'

            soup = BeautifulSoup(html, "html.parser")
            resources_dir = os.path.join(os.path.dirname(output_html), "resources")
            os.makedirs(resources_dir, exist_ok=True)

            # Helper to download and update resource links
            def download_resource(tag, attr, resource_type):
                src = tag.get(attr)
                if src and not src.startswith("data:"):
                    res_url = src if src.startswith("http") else self.base_url + src
                    res_name = os.path.basename(res_url.split("?")[0])
                    res_path = os.path.join(resources_dir, res_name)
                    try:
                        r = requests.get(res_url)
                        if r.status_code == 200:
                            with open(res_path, "wb") as f:
                                f.write(r.content)
                            tag[attr] = f"resources/{res_name}"
                        else:
                            print(f"Failed to download {resource_type} {res_url}: {r.status_code}")
                    except Exception as e:
                        print(f"Failed to download {resource_type} {res_url}: {e}")

            # Download images (png, jpg, jpeg, gif, webp, svg, etc.)
            for img in soup.find_all("img"):
                download_resource(img, "src", "image")

            # Download CSS files
            for link in soup.find_all("link", rel="stylesheet"):
                download_resource(link, "href", "css")

            # Download JS files
            for script in soup.find_all("script"):
                src = script.get("src")
                if src:
                    download_resource(script, "src", "js")

            # Download other resources (e.g., <link rel="icon">, <link rel="preload">, etc.)
            for link in soup.find_all("link"):
                href = link.get("href")
                if href and not link.get("rel") == ["stylesheet"]:
                    download_resource(link, "href", "link")

            # Download objects (e.g., <object data="...">)
            for obj in soup.find_all("object"):
                download_resource(obj, "data", "object")

            # Download embeds (e.g., <embed src="...">)
            for embed in soup.find_all("embed"):
                download_resource(embed, "src", "embed")

            # Download iframes (e.g., <iframe src="...">)
            for iframe in soup.find_all("iframe"):
                download_resource(iframe, "src", "iframe")

            # Save updated HTML with local resource links
            with open(output_html, "w", encoding="utf-8") as f:
                f.write(str(soup))
            print(f"Saved HTML with resources to {output_html}")
            return True
        else:
            print(f"Failed to fetch page: {response.status_code}")
            return False

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python download_pdf.py <PAGE_ID> <PAGE_TITLE> <BASE_URL> <EMAIL> <TOKEN>")
        sys.exit(1)

    downloader = HTMLDownloader(
        page_id=sys.argv[1],
        page_title=sys.argv[2],
        base_url=sys.argv[3],
        email=sys.argv[4],
        token=sys.argv[5]
    )
downloader.save_page_with_resources()