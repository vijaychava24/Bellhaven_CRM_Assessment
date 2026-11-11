
import json
import re
from rapidfuzz import fuzz

with open("crm_accounts.json", encoding="utf-8") as f:
    accounts = json.load(f)

with open("bellhaven_facilities.json", encoding="utf-8") as f:
    facilities = json.load(f)


def normalize(value):
    value = str(value or "").lower()
    value = re.sub(r"[^\w\s]", " ", value)
    return " ".join(value.split())


def match_facility(facility, accounts):
    candidates = []

    for account in accounts:
        name_score = fuzz.token_sort_ratio(
            normalize(facility["name"]),
            normalize(account.get("name"))
        )

        street_score = fuzz.token_sort_ratio(
            normalize(facility.get("street")),
            normalize(account.get("billing_street"))
        )

        city_match = (
            normalize(facility.get("city"))
            == normalize(account.get("billing_city"))
        )

        state_match = (
            normalize(facility.get("state"))
            == normalize(account.get("billing_state"))
        )

        zip_match = (
            str(facility.get("zip") or "").strip()
            == str(account.get("billing_zip") or "").strip()
        )

        score = (
            name_score * 0.40
            + street_score * 0.35
            + (10 if city_match else 0)
            + (5 if state_match else 0)
            + (10 if zip_match else 0)
        )

        candidates.append({
            "account_id": account.get("account_id"),
            "account_name": account.get("name"),
            "parent_id": account.get("parent_id"),
            "parent_name": account.get("parent_name"),
            "score": round(score, 2),
            "name_score": round(name_score, 2),
            "street_score": round(street_score, 2),
            "city_match": city_match,
            "state_match": state_match,
            "zip_match": zip_match
        })

    return sorted(
        candidates,
        key=lambda x: x["score"],
        reverse=True
    )[:3]


results = []

for facility in facilities:
    matches = match_facility(facility, accounts)
    best = matches[0] if matches else None

    if best and best["score"] >= 90:
        classification = "Strong candidate"
    elif best and best["score"] >= 70:
        classification = "Needs review"
    else:
        classification = "No reliable match"

    results.append({
        "facility": facility,
        "classification": classification,
        "best_match": best,
        "top_candidates": matches
    })

with open("matching_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\nMATCHING RESULTS")
print("=" * 45)

for classification in [
    "Strong candidate",
    "Needs review",
    "No reliable match"
]:
    count = sum(
        1 for item in results
        if item["classification"] == classification
    )
    print(f"{classification}: {count}")

print("\nSaved to matching_results.json")
