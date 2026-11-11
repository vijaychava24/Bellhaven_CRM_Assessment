
import json
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent

with open(BASE / "proposals.json", encoding="utf-8") as f:
    proposals = json.load(f)

decisions_path = BASE / "review_decisions.json"

if decisions_path.exists():
    with open(decisions_path, encoding="utf-8") as f:
        decisions = json.load(f)
else:
    decisions = {}

rows = []

for proposal in proposals:
    pid = proposal["proposal_id"]
    decision = decisions.get(pid, {})

    rows.append({
        "proposal_id": pid,
        "facility_name": proposal.get("facility_name"),
        "classification": proposal.get("classification"),
        "crm_account_name": proposal.get("crm_account_name"),
        "crm_account_id": proposal.get("crm_account_id"),
        "crm_parent_name": proposal.get("crm_parent_name"),
        "match_score": proposal.get("match_score"),
        "proposed_action": proposal.get("proposed_action"),
        "proposed_changes": json.dumps(
            proposal.get("proposed_changes") or {}
        ),
        "review_decision": decision.get("decision", "Pending"),
        "reviewer_note": decision.get("note", ""),
        "reason": proposal.get("reason", "")
    })

output = BASE / "final_review_report.csv"

with open(output, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print("FINAL REVIEW REPORT CREATED")
print("Total facilities:", len(rows))

print("Approved:", sum(r["review_decision"] == "Approved" for r in rows))
print("Rejected:", sum(r["review_decision"] == "Rejected" for r in rows))
print("Needs Investigation:", sum(
    r["review_decision"] == "Needs Investigation"
    for r in rows
))
print("Pending:", sum(r["review_decision"] == "Pending" for r in rows))
print("Saved to:", output)
