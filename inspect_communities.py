import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

BASE_URL = "https://analyst-assessment-production.up.railway.app"
DIRECTORY_URL = f"{BASE_URL}/communities"

facility_links = set()
visited_pages = set()
pages_to_visit = [DIRECTORY_URL]

session = requests.Session()

while pages_to_visit:
    page_url = pages_to_visit.pop(0)

    if page_url in visited_pages:
        continue

    if len(visited_pages) >= 100:
        raise RuntimeError("Pagination safety limit reached")

    print(f"\nChecking: {page_url}")

    response = session.get(page_url, timeout=30)
    response.raise_for_status()

    visited_pages.add(page_url)

    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.find_all("a", href=True):
        url = urljoin(page_url, link["href"])
        parsed = urlparse(url)

        if parsed.netloc != urlparse(BASE_URL).netloc:
            continue

        # Collect individual facility pages
        if parsed.path.startswith("/communities/"):
            facility_links.add(
                f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            )

        # Find additional directory pages
        elif parsed.path == "/communities":
            query = parse_qs(parsed.query)

            if "page" in query:
                if url not in visited_pages and url not in pages_to_visit:
                    pages_to_visit.append(url)

print("\n" + "=" * 50)
print("TOTAL DIRECTORY PAGES:", len(visited_pages))
print("TOTAL UNIQUE FACILITY LINKS:", len(facility_links))

with open("facility_links.txt", "w", encoding="utf-8") as file:
    for url in sorted(facility_links):
        file.write(url + "\n")

print("\nSaved facility links to facility_links.txt")