
import json
from pathlib import Path
from crm_client import get_accounts

BASE = Path(__file__).resolve().parent

proposals = json.loads(
    (BASE / "proposals.json").read_text(encoding="utf-8")
)

decisions = json.loads(
    (BASE / "review_decisions.json").read_text(encoding="utf-8")
)

accounts = get_accounts()

account_lookup = {
    str(a.get("account_id")): a
    for a in accounts
}

approved = [
    p for p in proposals
    if decisions.get(
        p["proposal_id"], {}
    ).get("decision") == "Approved"
]

print(f"\nApproved proposals: {len(approved)}")
print("Checking live CRM records...\n")

for proposal in approved:
    pid = proposal["proposal_id"]
    name = proposal.get("facility_name")
    action = proposal.get("proposed_action")
    changes = proposal.get("proposed_changes") or {}

    print(f"{pid}: {name}")

    if action == "VERIFY_STRONG_MATCH":
        print("  Match approved; no CRM field update defined.")
        continue

    if not changes:
        print("  No field changes defined. Skipping.")
        continue

    account_id = str(proposal.get("crm_account_id"))
    account = account_lookup.get(account_id)

    if not account:
        print("  CRM account not found. Skipping.")
        continue

    for field, proposed_value in changes.items():
        current_value = account.get(field)

        if str(current_value) == str(proposed_value):
            print(f"  {field}: Already correct. Skipping.")
        else:
            print(
                f"  {field}: {current_value} -> {proposed_value}"
            )
            print("  Requires validation before CRM update.")

print("\nDry run completed. No CRM records were changed.")

