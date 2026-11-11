
import json
from crm_client import get_accounts

accounts = get_accounts()

if accounts:
    account = accounts[0]

    print("\nFIRST CRM ACCOUNT:")
    print(json.dumps(account, indent=2))

    print("\nAVAILABLE FIELDS:")
    for field in account.keys():
        print(field)
else:
    print("No CRM accounts found.")
