import requests
from bs4 import BeautifulSoup
import os
import pikepdf

BASE = "https://www.assamboard.com"
MAIN = "https://www.assamboard.com/assam-deled.html"

ROOT_FOLDER = "pdf"

os.makedirs(ROOT_FOLDER, exist_ok=True)

# load main page
res = requests.get(MAIN)
soup = BeautifulSoup(res.text, "html.parser")

pages = []

for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/papers/" in href and href.endswith(".html"):
        pages.append(BASE + href)

pages = list(set(pages))

print("Found pages:", len(pages))

for page in pages:

    r = requests.get(page)
    soup = BeautifulSoup(r.text, "html.parser")

    pdf_tag = soup.find("a", id="pyq-hide-1s")

    if not pdf_tag:
        continue

    pdf_link = pdf_tag["href"]

    if not pdf_link.startswith("http"):
        pdf_link = BASE + "/papers/" + pdf_link

    filename = pdf_link.split("/")[-1]

    parts = filename.split("-")

    class_folder = f"{parts[0]}-{parts[1]}-{parts[2]}"
    year = parts[-1].replace(".pdf", "")

    year_path = os.path.join(ROOT_FOLDER, year)
    class_path = os.path.join(year_path, class_folder)

    os.makedirs(class_path, exist_ok=True)

    save_path = os.path.join(class_path, filename)

    if os.path.exists(save_path):
        print("Skip:", filename)
        continue

    print("Downloading:", filename)

    data = requests.get(pdf_link).content

    temp_file = "temp.pdf"

    with open(temp_file, "wb") as f:
        f.write(data)

    # clean pdf
    with pikepdf.open(temp_file) as pdf:

        # remove metadata
        pdf.docinfo = {}

        root = pdf.Root

        # remove redirect actions
        if "/OpenAction" in root:
            del root["/OpenAction"]

        if "/AA" in root:
            del root["/AA"]

        # remove link actions
        for page in pdf.pages:
            if "/Annots" in page:
                annots = page["/Annots"]
                for annot in annots:
                    obj = annot.get_object()
                    if "/A" in obj:
                        del obj["/A"]

        pdf.save(save_path)

    os.remove(temp_file)

print("Scraping completed.")
