
import json
import re
from pathlib import Path


def normalize_street(value):
    value = str(value or "").lower().strip()

    replacements = {
        "boulevard": "blvd",
        "road": "rd",
        "avenue": "ave",
        "street": "st",
        "drive": "dr",
        "lane": "ln",
        "northwest": "nw",
        "northeast": "ne",
        "southwest": "sw",
        "southeast": "se",
        "west": "w",
        "north": "n",
        "south": "s",
        "east": "e",
    }

    value = re.sub(r"[.,]", "", value)

    return " ".join(
        replacements.get(word, word)
        for word in value.split()
    )


BASE = Path(__file__).resolve().parent

with open(BASE / "matching_results.json", encoding="utf-8") as f:
    matches = json.load(f)

with open(BASE / "crm_accounts.json", encoding="utf-8") as f:
    crm_data = json.load(f)

# Support either a plain list or the paginated CRM response.
if isinstance(crm_data, list):
    accounts = crm_data
elif isinstance(crm_data, dict):
    accounts = crm_data.get("data", [])
else:
    raise ValueError("Unexpected CRM accounts format")

accounts_by_id = {
    str(account["account_id"]): account
    for account in accounts
    if account.get("account_id")
}

proposals = []

for result in matches:
    facility = result.get("facility") or {}
    classification = result.get("classification", "Needs review")
    best = result.get("best_match") or {}

    account_id = str(best.get("account_id") or "")
    account = accounts_by_id.get(account_id, {})

    score = best.get("score", 0)
    zip_matches = best.get("zip_match", False)
    street_score = best.get("street_score", 0)

    if classification == "No reliable match":
        action = "INVESTIGATE_MISSING_ACCOUNT"
        reason = (
            "No reliable CRM match was identified. "
            "Verify existing accounts before creating a new one."
        )
    elif classification == "Needs review":
        action = "REVIEW_ACCOUNT_MATCH"
        reason = (
            "Matching evidence is inconclusive. "
            "Verify the account identity and parent relationship."
        )
    else:
        action = "VERIFY_STRONG_MATCH"
        reason = (
            "Strong matching candidate. Confirm the facility identity, "
            "parent ownership, and CRM data before proposing changes."
        )


       
    # Build proposed changes from verified website data.
    # This script does not write anything to the CRM.

    proposed_changes = {}
    website_parent_id = None

    if classification == "No reliable match":
        action = "INVESTIGATE_MISSING_ACCOUNT"

    elif classification == "Needs review":
        action = "REVIEW_ACCOUNT_MATCH"

    elif classification == "Strong candidate" and account:
        # Compare the website address against the CRM.
        field_mapping = {
            "street": "billing_street",
            "city": "billing_city",
            "state": "billing_state",
            "zip": "billing_zip",
        }

        for website_field, crm_field in field_mapping.items():
            website_value = str(
                facility.get(website_field) or ""
            ).strip()

            crm_value = str(
                account.get(crm_field) or ""
            ).strip()

            # Propose only nonempty website values that differ.
         
            if not website_value:
                continue

            if crm_field == "billing_street":
                is_different = (
                    normalize_street(website_value)
                    != normalize_street(crm_value)
                )
            else:
                is_different = (
                    website_value.casefold()
                    != crm_value.casefold()
                )

            if is_different:
                proposed_changes[crm_field] = website_value
   

        if proposed_changes:
            action = "REVIEW_FIELD_CORRECTIONS"
            reason = (
                "Strong CRM candidate with address differences. "
                "Verify that the website address is the correct "
                "CRM billing address before approving."
            )
        else:
            action = "VERIFY_STRONG_MATCH"
            reason = (
                "Strong CRM candidate with no address differences "
                "identified. Verify identity and ownership."
            )

    else:
        action = "REVIEW_ACCOUNT_MATCH"

    # Parent ownership is not inferred from facility names.
    # A parent_id correction requires independent evidence.

    proposals.append({
        "proposal_id": f"facility-{len(proposals) + 1:03d}",
        "facility_name": facility.get("name"),
        "website_address": {
            "street": facility.get("street"),
            "city": facility.get("city"),
            "state": facility.get("state"),
            "zip": facility.get("zip"),
        },
        "website_url": facility.get("source_url"),
        "classification": classification,
        "proposed_action": action,
        "reason": reason,
        "proposed_changes": proposed_changes,
        "website_parent_id": website_parent_id,
        "crm_account_id": account_id or None,
        "crm_account_name": best.get("account_name"),
        "crm_parent_id": account.get("parent_id"),
        "crm_parent_name": best.get("parent_name"),
        "match_score": score,
        "street_score": street_score,
        "zip_matches": zip_matches,
        "lifetime_revenue": account.get("lifetime_revenue"),
        "outstanding_ar": account.get("outstanding_ar"),
        "top_candidates": result.get("top_candidates", []),
        "review_status": "Pending",
    })

output_path = BASE / "proposals.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(proposals, f, indent=2)

print("PROPOSAL GENERATION COMPLETE")
print("=" * 45)
print(f"CRM accounts loaded: {len(accounts)}")
print(f"Facilities processed: {len(matches)}")
print(f"Review proposals created: {len(proposals)}")

for action in sorted(set(p["proposed_action"] for p in proposals)):
    count = sum(p["proposed_action"] == action for p in proposals)
    print(f"{action}: {count}")

print(f"\nSaved to: {output_path.name}")
