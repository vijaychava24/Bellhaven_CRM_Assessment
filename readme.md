
# Bellhaven CRM Reconciliation Assessment

## Project Overview
A Python-based workflow for reconciling Bellhaven Senior Living facility information with CRM accounts.

## Features
- Facility website data collection
- CRM account retrieval through API
- Facility-to-CRM matching
- Discrepancy identification
- Review dashboard built with Streamlit
- Reviewer approval tracking
- CRM change comparison and reporting

## Project Structure
- `app.py` - Streamlit review application
- `facility_scraper.py` - Facility data collection
- `crm_client.py` - CRM API integration
- `matching.py` - Facility matching logic
- `generate_proposals.py` - Reconciliation proposals
- `review_matches.py` - Review workflow
- `final_review_report.py` - Reporting

## Installation
Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Running the Application
```bash
streamlit run app.py
```

## Configuration
Provide the required CRM API credentials using environment variables or a local `.env` file.

Never commit API credentials to GitHub.

## Review Process
The workflow identifies proposed CRM changes for review. Reviewers can approve changes or flag them for investigation.

## Future Improvements
- Automated scheduled reconciliation
- Additional matching validation
- Expanded reporting and audit logging
