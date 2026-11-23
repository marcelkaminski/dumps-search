import requests
from bs4 import BeautifulSoup
import json

def get_first_google_result(query):
    import http.client

    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = ''
    headers = {}
    conn.request("GET", f"/search?q={query}&apiKey=<API_KEY>", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data_decoded = json.loads(data.decode("utf-8"))
    organic_links = [item["link"] for item in data_decoded["organic"] if "link" in item]
    return organic_links


if __name__ == "__main__":
    links = []
    try:
        for i in range(1, 560):
            print(i)
            search_query = f"site:examtopics.com+intitle:Associate+DVA-C02+topic+1+question+{i}+discussion"
            organic_links = get_first_google_result(search_query)
            links.extend(organic_links)
    finally:
        with open("raw_links.json", "w", encoding="utf-8") as f:
            json.dump(links, f, ensure_ascii=False, indent=4)
