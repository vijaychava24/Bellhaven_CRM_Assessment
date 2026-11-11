import json
import requests
from crm_client import BASE_URL, HEADERS

all_accounts = []
page = 1
page_size = 50

while True:
    print(f"Fetching page {page}...")

    response = requests.get(
        f"{BASE_URL.rstrip('/')}/accounts",
        headers=HEADERS,
        params={
            "page": page,
            "page_size": page_size
        },
        timeout=30
    )

    response.raise_for_status()
    result = response.json()

    accounts = result.get("data", [])

    if not isinstance(accounts, list):
        raise ValueError("Unexpected CRM response structure")

    all_accounts.extend(accounts)

    print(f"Retrieved {len(accounts)} accounts")

    total = result.get("total")

    if total is not None and len(all_accounts) >= total:
        break

    if not accounts or len(accounts) < page_size:
        break

    page += 1

print("\nTOTAL CRM ACCOUNTS:", len(all_accounts))

if all_accounts:
    print("\nACCOUNT FIELDS:")
    print(list(all_accounts[0].keys()))

    with open("crm_accounts.json", "w", encoding="utf-8") as file:
        json.dump(all_accounts, file, indent=2)

    print("\nSuccessfully saved CRM accounts!")