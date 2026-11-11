import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://analyst-assessment-production.up.railway.app"

def inspect_website():
    response = requests.get(BASE_URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    print("Website status:", response.status_code)
    print("Page title:", soup.title.get_text(strip=True) if soup.title else "None")

    print("\nLinks found on website:")
    for link in soup.find_all("a", href=True):
        text = link.get_text(" ", strip=True)
        url = urljoin(BASE_URL, link["href"])

        if text:
            print(f"{text}: {url}")

    print("\nPotential facility-related sections:")
    for heading in soup.find_all(["h1", "h2", "h3"]):
        print(heading.get_text(" ", strip=True))

if __name__ == "__main__":
    inspect_website()