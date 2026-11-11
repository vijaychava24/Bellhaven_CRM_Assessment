
import json
from pathlib import Path
import streamlit as st

BASE = Path(__file__).resolve().parent
PROPOSALS_FILE = BASE / "proposals.json"
DECISIONS_FILE = BASE / "review_decisions.json"

st.set_page_config(
    page_title="Bellhaven CRM Review",
    page_icon="🏥",
    layout="wide"
)

def load_json(path, default):
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default

def save_decisions(decisions):
    with open(DECISIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2)

proposals = load_json(PROPOSALS_FILE, [])
decisions = load_json(DECISIONS_FILE, {})

st.title("Bellhaven CRM Review Dashboard")
st.write("Review website facilities and CRM matching evidence.")

total = len(proposals)
approved = sum(
    d.get("decision") == "Approved"
    for d in decisions.values()
)
rejected = sum(
    d.get("decision") == "Rejected"
    for d in decisions.values()
)

investigation = sum(
    d.get("decision") == "Needs Investigation"
    for d in decisions.values()
)

pending = total - approved - rejected - investigation

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Proposals", total)
col2.metric("Approved", approved)
col3.metric("Rejected", rejected)
col4.metric("Needs Investigation", investigation)
col5.metric("Pending", pending)

st.divider()

for proposal in proposals:
    pid = proposal["proposal_id"]
    facility_name = proposal.get("facility_name", "Unknown")
    classification = proposal.get("classification", "")
    action = proposal.get("proposed_action", "")
    existing = decisions.get(pid, {})

    with st.expander(
        f"{facility_name} | {classification} | "
        f"{existing.get('decision', 'Pending')}"
    ):
        st.subheader("Website Information")
        st.write("Facility:", facility_name)
        
        address = proposal.get("website_address") or {}

        st.write(
            "Address:",
            ", ".join(
                str(address.get(field))
                for field in ("street", "city", "state", "zip")
                if address.get(field)
            )
        )

        st.write("Website:", proposal.get("website_url"))

        st.subheader("CRM Matching Evidence")
        st.write("CRM Account:", proposal.get("crm_account_name"))
        st.write("Account ID:", proposal.get("crm_account_id"))
        st.write("Parent:", proposal.get("crm_parent_name"))
        st.write("Match Score:", proposal.get("match_score"))
        st.write("Street Score:", proposal.get("street_score"))
        st.write("ZIP Matches:", proposal.get("zip_matches"))

        st.subheader("Billing Information")
        st.write("Lifetime Revenue:", proposal.get("lifetime_revenue"))
        st.write("Outstanding AR:", proposal.get("outstanding_ar"))

        st.subheader("Proposed Action")
        st.info(action)
        st.write(proposal.get("reason"))

        st.subheader("Alternative CRM Candidates")
        st.json(proposal.get("top_candidates", []))

        note = st.text_area(
            "Reviewer Notes",
            value=existing.get("note", ""),
            key=f"note_{pid}"
        )

        
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("Approve", key=f"approve_{pid}"):
                decisions[pid] = {
                    "decision": "Approved",
                    "note": note
                }
                save_decisions(decisions)
                st.rerun()

        with col_b:
            if st.button("Reject", key=f"reject_{pid}"):
                decisions[pid] = {
                    "decision": "Rejected",
                    "note": note
                }
                save_decisions(decisions)
                st.rerun()

        with col_c:
            if st.button(
                "Needs Investigation",
                key=f"investigate_{pid}"
            ):
                decisions[pid] = {
                    "decision": "Needs Investigation",
                    "note": note
                }
                save_decisions(decisions)
                st.rerun()




st.divider()


st.header("Approved CRM Changes")

approved_proposals = [
    p for p in proposals
    if decisions.get(
        p["proposal_id"], {}
    ).get("decision") == "Approved"
]

st.metric("Approved Proposals", len(approved_proposals))

if approved_proposals:
    for proposal in approved_proposals:
        with st.expander(proposal["facility_name"]):
            st.write(
                "Proposed Action:",
                proposal.get("proposed_action")
            )
            st.write(
                "CRM Account:",
                proposal.get("crm_account_name")
            )
            st.write(
                "Account ID:",
                proposal.get("crm_account_id")
            )
            st.write(
                "Parent:",
                proposal.get("crm_parent_name")
            )
            st.write(
                "Match Score:",
                proposal.get("match_score")
            )

            
            st.subheader("Exact CRM Change Preview")

            changes = proposal.get("proposed_changes") or {}

            if changes:
                st.warning(
                    "Proposed corrections require verification. "
                    "Website addresses may differ from CRM billing addresses."
                )

                crm_data = load_json(BASE / "crm_accounts.json", [])
                accounts = (
                    crm_data if isinstance(crm_data, list)
                    else crm_data.get("data", [])
                )

                account = next(
                    (
                        a for a in accounts
                        if str(a.get("account_id")) ==
                        str(proposal.get("crm_account_id"))
                    ),
                    {}
                )

                for field, new_value in changes.items():
                    current_value = account.get(field)

                    st.write("**Field:**", field)
                    st.write("**Current CRM Value:**", current_value)
                    st.write("**Proposed Value:**", new_value)
                    st.write("**Verification Status:** Needs Verification")
                    st.divider()
            else:
                st.info(
                    "No CRM field changes have been defined. "
                    "This proposal requires verification before "
                    "any CRM update can be applied."
                )


    
    st.subheader("Live CRM Verification")

    if st.button("Verify Approved Changes in CRM"):
        from crm_client import get_accounts

        with st.spinner("Checking live CRM records..."):
            try:
                accounts = get_accounts()
                account_lookup = {
                    str(a.get("account_id")): a
                    for a in accounts
                }

                checked = 0
                verified = 0
                differences = []

                for proposal in approved_proposals:
                    changes = proposal.get("proposed_changes") or {}

                    if not changes:
                        continue

                    checked += 1
                    account = account_lookup.get(
                        str(proposal.get("crm_account_id"))
                    )

                    if account is None:
                        differences.append(
                            f"{proposal['facility_name']}: "
                            "CRM account not found"
                        )
                        continue

                    if all(
                        str(account.get(field)) == str(value)
                        for field, value in changes.items()
                    ):
                        verified += 1
                    else:
                        differences.append(
                            f"{proposal['facility_name']}: "
                            "CRM values do not match proposed changes"
                        )

                st.success(
                    f"Verified {verified} of {checked} "
                    "approved proposals with field changes."
                )

                for difference in differences:
                    st.warning(difference)

                if checked == 0:
                    st.info(
                        "No approved proposals require field changes."
                    )

            except Exception as error:
                st.error(
                    f"CRM verification failed: {error}"
                )


else:
    st.info("No approved proposals yet.")

st.caption(
    "All CRM changes require separate confirmation."
)


