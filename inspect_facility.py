import requests
from bs4 import BeautifulSoup

with open("facility_links.txt", "r", encoding="utf-8") as file:
    urls = [line.strip() for line in file if line.strip()]

if not urls:
    raise ValueError("No facility URLs found.")

url = urls[0]

print("Inspecting facility:", url)

response = requests.get(url, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Remove scripts and styling from the visible text
for element in soup(["script", "style", "nav", "footer"]):
    element.decompose()

print("\nPAGE HEADINGS")
print("=" * 50)

for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
    print(heading.get_text(" ", strip=True))

print("\nADDRESS ELEMENTS")
print("=" * 50)

for address in soup.find_all("address"):
    print(address.get_text(" ", strip=True))

print("\nSTRUCTURED ADDRESS INFORMATION")
print("=" * 50)

for element in soup.select(
    '[itemprop="streetAddress"], '
    '[itemprop="addressLocality"], '
    '[itemprop="addressRegion"], '
    '[itemprop="postalCode"]'
):
    print(element.get("itemprop"), ":", element.get_text(" ", strip=True))

print("\nVISIBLE PAGE TEXT")
print("=" * 50)

text = soup.get_text("\n", strip=True)

print(text[:6000])