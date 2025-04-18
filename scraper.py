import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    "User-Agent": "Mozilla/5.0"
}
   
def scrape_data(url):
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    script_tag = soup.find("script", string=re.compile("var pdpTrackingData ="))
    pattern = r"var pdpTrackingData\s*=\s*\"(.*?)\";"
    match = re.search(pattern, script_tag.string)
    if match:
        json_str = match.group(1)
        # Unescape the string
        json_str = bytes(json_str, "utf-8").decode("unicode_escape")
        data = json.loads(json_str)
        name = data.get("pdt_name")
        price = data.get("pdt_price")
        price = price.split()
        price = price[1].replace(",", "") 
        return name, price
    else:
        name = ""
        price = ""
        return name, price
        