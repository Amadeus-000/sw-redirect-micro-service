import requests
import os
def fetch_redirect_url(work_id: str)-> str|None:
    API_KEY = os.environ.get("MICRO_CMS_API_KEY")
    if not API_KEY:
        raise ValueError("MICRO_CMS_API_KEY environment variable is not set")
    response = requests.get(
        url ="https://sw-app.microcms.io/api/v1/redirect", 
        headers={
            "X-MICROCMS-API-KEY": API_KEY,
        },
            params={
            "filters": f"work_id[equals]{work_id}",
            "limit": 1,
        }
    )
    response.raise_for_status()
    data = response.json()
    contents = data.get("contents", [])
    return contents[0]["redirect_url"] if contents else None