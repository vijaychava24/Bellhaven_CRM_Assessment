
import requests
import json

URL = "https://analyst-assessment-production.up.railway.app/api/openapi.json"

response = requests.get(URL, timeout=30)
response.raise_for_status()
schema = response.json()

for path, methods in schema.get("paths", {}).items():
    if path.startswith("/api/v1/accounts"):
        for method, details in methods.items():
            print("\n" + "=" * 50)
            print(method.upper(), path)
            print("Summary:", details.get("summary"))
            print("Request body:")
            print(json.dumps(
                details.get("requestBody", "Not documented"),
                indent=2
            ))

print("\nACCOUNT-RELATED SCHEMAS:")
for name, definition in schema.get(
    "components", {}
).get("schemas", {}).items():
    if "account" in name.lower():
        print(name)
        print(json.dumps(definition, indent=2))
