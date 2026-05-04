import sys
import os
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class HTMLToPDF:
    def __init__(self, html_path):
        self.html_path = html_path
        self.resources_dir = os.path.join(os.path.dirname(html_path), "resources")
        self.pdf_path = html_path.replace(".html", ".pdf")

    def _get_images(self, soup):
        images = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and not src.startswith("data:"):
                img_path = os.path.join(self.resources_dir, os.path.basename(src))
                if os.path.exists(img_path):
                    images.append(img_path)
        return images

    def generate_pdf(self):
        with open(self.html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        c = canvas.Canvas(self.pdf_path, pagesize=letter)
        width, height = letter
        y = height - 40  # Start a bit below the top

        # Add text content
        for element in soup.find_all(["h1", "h2", "h3", "p", "li"]):
            text = element.get_text(strip=True)
            if text:
                font_size = 12
                if element.name == "h1":
                    font_size = 18
                elif element.name == "h2":
                    font_size = 16
                elif element.name == "h3":
                    font_size = 14
                c.setFont("Helvetica", font_size)
                for line in text.splitlines():
                    c.drawString(40, y, line)
                    y -= font_size + 4
                    if y < 60:
                        c.showPage()
                        y = height - 40

        # Add images
        images = self._get_images(soup)
        for img_path in images:
            try:
                c.showPage()
                img = ImageReader(img_path)
                iw, ih = img.getSize()
                aspect = ih / float(iw)
                img_width = width - 80
                img_height = img_width * aspect
                c.drawImage(img, 40, height - img_height - 40, width=img_width, height=img_height)
            except Exception as e:
                print(f"Failed to add image {img_path}: {e}")

        c.save()
        print(f"PDF generated: {self.pdf_path}")
        return self.pdf_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python html_to_pdf.py <HTML_FILE_PATH>")
        sys.exit(1)
    converter = HTMLToPDF(sys.argv[1])
    converter.generate_pdf()