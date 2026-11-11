
import json
import re
import time
import requests
from bs4 import BeautifulSoup

INPUT_FILE = "facility_links.txt"
OUTPUT_FILE = "bellhaven_facilities.json"

session = requests.Session()
session.headers.update({
    "User-Agent": "BellhavenCRMAssessment/1.0"
})


def extract_facility(url):
    response = session.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()

    heading = soup.find("h1")
    name = heading.get_text(" ", strip=True) if heading else None

    lines = [
        line.strip()
        for line in soup.get_text("\n", strip=True).splitlines()
        if line.strip()
    ]

    street = None
    city = None
    state = None
    zip_code = None
    care_offerings = []

    if "Address" in lines:
        index = lines.index("Address")

        if index + 2 < len(lines):
            street = lines[index + 1]
            location = lines[index + 2]

            match = re.match(
                r"^(.+?),\s*([A-Z]{2})\s+(\d{5})(?:-\d{4})?$",
                location
            )

            if match:
                city = match.group(1)
                state = match.group(2)
                zip_code = match.group(3)

    if "Care Offerings" in lines:
        index = lines.index("Care Offerings") + 1

        stop_labels = {
            "Administrator",
            "Phone",
            "Address",
            "Back to all communities"
        }

        while index < len(lines):
            value = lines[index]

            if value in stop_labels or value.startswith("←"):
                break

            care_offerings.append(value)
            index += 1

    return {
        "name": name,
        "street": street,
        "city": city,
        "state": state,
        "zip": zip_code,
        "care_offerings": care_offerings,
        "source_url": url
    }


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        urls = sorted(set(
            line.strip()
            for line in file
            if line.strip()
        ))

    facilities = []
    errors = []

    for number, url in enumerate(urls, start=1):
        print(f"Scraping {number}/{len(urls)}: {url}")

        try:
            facility = extract_facility(url)
            facilities.append(facility)

        except requests.RequestException as error:
            errors.append({
                "url": url,
                "error": str(error)
            })
            print("FAILED:", type(error).__name__)

        time.sleep(0.2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(facilities, file, indent=2)

    print("\nSCRAPING RESULTS")
    print("=" * 45)
    print("Facility URLs:", len(urls))
    print("Successfully scraped:", len(facilities))
    print("Request failures:", len(errors))

    required = ["name", "street", "city", "state", "zip"]

    incomplete = [
        facility for facility in facilities
        if any(not facility.get(field) for field in required)
        or not facility["care_offerings"]
    ]

    print("Facilities with missing information:", len(incomplete))

    for facility in incomplete:
        print("CHECK:", facility["source_url"])

    if errors:
        with open("scraper_errors.json", "w", encoding="utf-8") as file:
            json.dump(errors, file, indent=2)

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
