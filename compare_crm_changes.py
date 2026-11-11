
import json
import csv
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
    words = value.split()

    return " ".join(
        replacements.get(word, word)
        for word in words
    )


BASE = Path(__file__).resolve().parent

DECISIONS_FILE = BASE / "review_decisions.json"

if DECISIONS_FILE.exists():
    with open(DECISIONS_FILE, encoding="utf-8") as f:
        decisions = json.load(f)
else:
    decisions = {}

with open(BASE / "proposals.json", encoding="utf-8") as f:
    proposals = json.load(f)

with open(BASE / "crm_accounts.json", encoding="utf-8") as f:
    crm_data = json.load(f)

accounts = (
    crm_data if isinstance(crm_data, list)
    else crm_data.get("data", [])
)

accounts_by_id = {
    str(a["account_id"]): a
    for a in accounts
    if a.get("account_id")
}

rows = []


for proposal in proposals:
    changes = proposal.get("proposed_changes") or {}

    if not changes:
        continue

    account_id = str(proposal.get("crm_account_id") or "")
    account = accounts_by_id.get(account_id)

    if not account:
        print("Account not found:", account_id)
        continue

    for field, new_value in changes.items():
        current_value = account.get(field)

        if field == "billing_street":
            if normalize_street(current_value) == normalize_street(new_value):
                continue

        rows.append({
            "proposal_id": proposal["proposal_id"],
            "facility": proposal["facility_name"],
            "crm_account_id": account_id,
            "field": field,
            "current_crm_value": current_value,
            "proposed_value": new_value,
            "match_score": proposal.get("match_score"),
            "review_status": decisions.get(
                proposal["proposal_id"], {}
             ).get("decision", "Pending"),
             "reviewer_note": decisions.get(
                 proposal["proposal_id"], {}
             ).get("note", ""),
            "verification_status": "Needs Verification"
        })


output = BASE / "crm_change_comparison.csv"

with open(output, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=[
    "proposal_id",
    "facility",
    "crm_account_id",
    "field",
    "current_crm_value",
    "proposed_value",
    "match_score",
    "review_status",
    "reviewer_note",
    "verification_status"
])
    writer.writeheader()
    writer.writerows(rows)

print("Comparison report created successfully!")
print("Fields requiring review:", len(rows))
print("Saved to:", output)
