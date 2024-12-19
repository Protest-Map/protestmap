# # Categories to add
# categories = [
#     "Protest", "March/Rally", "Strike", "Direct Action", "Study Circle", "Community Engagement", "Conference/Congress", "Mutual Aid Call", "Everyday Resistance",
#     "Local Branch/Chapter", "Progressive Community Space", "Worker Cooperative", "Communal Housing"
# ]

# # Add categories
# for category in categories:
#     response = requests.post(f"{BASE_URL}/categories", json={"name": category})
#     print(f"Response status code: {response.status_code}")
#     print(f"Response text: {response.text}")
#     if response.status_code == 201:
#         print(f"Added category: {category}")
#     else:
#         print(f"Failed to add category: {category}. Error: {response.text}")

import requests

# Base URL of your Flask app
BASE_URL = "http://127.0.0.1:5000/api"

# Tags to add
tags = [
    "Queer Liberation", "Pride", "Trans Rights", "LGBTQ2SIA+ Rights",
    "Women's Liberation", "Domestic Violence", "#MeToo", "Gender Equality",
    "Anti-Racism", "BLM", "Black Liberation", "Anti-War",
    "Environmental Justice", "Climate Action", "Climate Strike", "Workers’ Rights",
    "Labor Movement", "Anti-Capitalist", "Anti-Privatization", "Cost of Living",
    "Inflation", "Pro-Democracy", "Free Palestine", "Kashmir", "Indigenous Rights",
    "Decolonization", "Refugee Rights", "Anti-Imperialism", "Free Education",
    "Healthcare for All", "Student Movement", "Youth Movement", "Immigrant Rights",
    "Abolish Prisons", "Land Back", "No Borders", "Anti-Fascism",
    "Anti-Authoritarianism", "Missing Persons", "Disability Justice",
    "Housing for All", "Rent Control"
]


# Add tags
for tag in tags:
    response = requests.post(f"{BASE_URL}/tags", json={"name": tag})
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")
    if response.status_code == 201:
        print(f"Added tag: {tag}")
    else:
        print(f"Failed to add tag: {tag}. Error: {response.json()}")