
import json
import csv

with open("matching_results.json", encoding="utf-8") as f:
    results = json.load(f)

with open("crm_accounts.json", encoding="utf-8") as f:
    accounts = json.load(f)

account_lookup = {
    str(account["account_id"]): account
    for account in accounts
}

rows = []

for result in results:
    facility = result["facility"]
    best = result.get("best_match") or {}

    account = account_lookup.get(
        str(best.get("account_id")), {}
    )

    row = {
        "facility_name": facility.get("name"),
        "facility_address": facility.get("street"),
        "facility_city": facility.get("city"),
        "facility_state": facility.get("state"),
        "facility_zip": facility.get("zip"),
        "classification": result.get("classification"),
        "matched_account_id": best.get("account_id"),
        "matched_account_name": best.get("account_name"),
        "matching_score": best.get("score"),
        "name_score": best.get("name_score"),
        "street_score": best.get("street_score"),
        "zip_match": best.get("zip_match"),
        "parent_id": account.get("parent_id"),
        "parent_name": account.get("parent_name"),
        "account_status": account.get("status"),
        "lifetime_revenue": account.get("lifetime_revenue"),
        "outstanding_ar": account.get("outstanding_ar"),
        "source_url": facility.get("source_url")
    }

    rows.append(row)

output_file = "matching_review.csv"

with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("MATCHING REVIEW REPORT")
print("=" * 45)
print("Total facilities:", len(rows))
print("Report saved:", output_file)

print("\nFACILITIES REQUIRING ATTENTION")
print("=" * 45)

for row in rows:
    if row["classification"] != "Strong candidate":
        print(
            f'{row["facility_name"]} | '
            f'{row["classification"]} | '
            f'Score: {row["matching_score"]} | '
            f'CRM: {row["matched_account_name"]}'
        )
