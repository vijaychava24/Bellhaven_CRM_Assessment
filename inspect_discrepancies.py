
import json

with open("matching_results.json", encoding="utf-8") as f:
    results = json.load(f)

with open("crm_accounts.json", encoding="utf-8") as f:
    accounts = json.load(f)

account_lookup = {
    str(a["account_id"]): a
    for a in accounts
}

for result in results:
    if result["classification"] == "Strong candidate":
        continue

    facility = result["facility"]

    print("\n" + "=" * 65)
    print("WEBSITE FACILITY:", facility["name"])
    print("=" * 65)

    print(
        "Website address:",
        facility.get("street"),
        facility.get("city"),
        facility.get("state"),
        facility.get("zip")
    )

    print("Website URL:", facility.get("source_url"))

    for number, candidate in enumerate(
        result.get("top_candidates", []), start=1
    ):
        account = account_lookup.get(
            str(candidate["account_id"])
        )

        if not account:
            continue

        print(f"\nCRM CANDIDATE {number}")
        print("-" * 45)

        print("Account ID:", account.get("account_id"))
        print("Account name:", account.get("name"))

        print(
            "CRM address:",
            account.get("billing_street"),
            account.get("billing_city"),
            account.get("billing_state"),
            account.get("billing_zip")
        )

        print("Match score:", candidate["score"])
        print("Name score:", candidate["name_score"])
        print("Street score:", candidate["street_score"])
        print("ZIP matches:", candidate["zip_match"])

        print("Parent ID:", account.get("parent_id"))
        print("Parent name:", account.get("parent_name"))
        print("Status:", account.get("status"))

        print("Lifetime revenue:", account.get("lifetime_revenue"))
        print("Outstanding AR:", account.get("outstanding_ar"))
        print("CHOW current account:", account.get("chow_current_account"))
        print("Duplicate of:", account.get("duplicate_of_account"))
