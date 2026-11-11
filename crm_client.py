import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CRM_BASE_URL")
API_TOKEN = os.getenv("CRM_API_TOKEN")

if not BASE_URL or not API_TOKEN:
    raise ValueError("Missing CRM configuration in .env")

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}



def get_accounts():
    all_accounts = []
    page = 1

    while True:
        url = f"{BASE_URL.rstrip('/')}/accounts"

        response = requests.get(
            url,
            headers=HEADERS,
            params={"page": page, "page_size": 50},
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        accounts = result.get("data", [])
        all_accounts.extend(accounts)

        print(f"Page {page}: Retrieved {len(accounts)} accounts")

        total = result.get("total", 0)

        if not accounts or len(all_accounts) >= total:
            break

        page += 1

    return all_accounts



def crm_request(method, endpoint, payload=None):
    url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

    response = requests.request(
        method=method,
        url=url,
        headers={
            **HEADERS,
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    if not response.content:
        return None

    return response.json()


def create_account(payload):
    """Create a CRM account after reviewer approval."""
    return crm_request(
        "POST",
        "/accounts",
        payload
    )


def update_account(account_id, payload):
    """Update a CRM account after reviewer approval."""
    if not account_id:
        raise ValueError("Account ID is required")

    return crm_request(
        "PATCH",
        f"/accounts/{account_id}",
        payload
    )




if __name__ == "__main__":
    try:
        data = get_accounts()

        print("Successfully connected to Bellhaven CRM!")

        if isinstance(data, list):
            print("Accounts returned:", len(data))
            if data:
                print("First account field names:", list(data[0].keys()))

        elif isinstance(data, dict):
            print("Response field names:", list(data.keys()))
            print("Total CRM accounts:", data.get("total"))
            print("Current page:", data.get("page"))
            print("Accounts on this page:", len(data.get("data", [])))

        else:
            print("Unexpected response format:", type(data).__name__)

    except requests.exceptions.HTTPError as error:
        print("CRM HTTP error:", error.response.status_code)

    except requests.exceptions.RequestException as error:
        print("CRM connection error:", type(error).__name__)

    except Exception as error:
        print("Error:", str(error))