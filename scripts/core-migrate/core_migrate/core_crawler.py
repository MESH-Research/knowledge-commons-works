import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import xmltodict


def get_desc_metadata(url):
    response = requests.get(url)
    from pprint import pprint

    # Parse the XML response into a dictionary
    data = xmltodict.parse(response.content)
    pprint(data)

    def make_name(name):
        name_item = {
            "type": name["@type"],
            "first_name": name["namePart"][1]["#text"],
            "last_name": name["namePart"][0]["#text"],
        }
        if "affiliation" in name.keys():
            name_item["affiliation"] = name["affiliation"]
        if "role" in name.keys():
            name_item["role"] = name["role"]["roleTerm"]["#text"]
        return name_item

    meta = {}
    mods = data["mods"]
    meta["title"] = mods["titleInfo"]["title"]
    print("a")
    if type(mods["name"]) is list:
        meta["name"] = []
        for n in mods["name"]:
            meta["name"].append(make_name(n))
    else:
        meta["name"] = [make_name(mods["name"])]
    meta["item type"] = mods["genre"]
    meta["date"] = mods["originInfo"]["dateIssued"]["#text"]
    if "abstract" in mods.keys():
        meta["abstract"] = mods["abstract"]
    if "language" in mods.keys():
        meta["language"] = mods["language"]["languageTerm"]["#text"]
    if "relatedItem" in mods.keys():
        r = mods["relatedItem"]
        if "titleInfo" in r.keys():
            meta["journal"] = r["titleInfo"]["title"]
        if "originInfo" in r.keys():
            meta["publisher"] = r["originInfo"]["publisher"]
        if "part" in r.keys():
            vol = [p for p in r["part"]["detail"] if p["@type"] == "volume"]
            if len(vol) > 0:
                meta["volume"] = vol[0]["number"]
            issue = [p for p in r["part"]["detail"] if p["@type"] == "issue"]
            if len(issue) > 0:
                meta["issue"] = issue[0]["number"]
            if "extent" in r["part"].keys():
                if "start" in r["part"]["extent"].keys():
                    meta["page start"] = r["part"]["extent"]["start"]
                if "end" in r["part"]["extent"].keys():
                    meta["page end"] = r["part"]["extent"]["end"]
                if "date" in r["part"].keys():
                    meta["published date"] = r["part"]["date"]
    if "identifier" in mods.keys():
        for identifier in mods["identifier"]:
            if identifier["@type"] == "doi":
                meta["doi"] = identifier["#text"]
            if identifier["@type"] == "isbn":
                meta["isbn"] = identifier["#text"]
            if identifier["@type"] == "issn":
                meta["issn"] = identifier["#text"]

    # Return the dictionary
    return meta


def get_metadata(record_id):
    op = webdriver.ChromeOptions()
    op.add_argument("headless")
    driver = webdriver.Chrome(options=op)
    driver.get(f"https://hcommons.org/deposits/item/{record_id}")

    metadata = {}
    meta_desc = {}

    titles = driver.find_elements(By.CSS_SELECTOR, ".bp-group-documents-title")
    metadata["title"] = titles[0].text

    meta = driver.find_elements(By.CSS_SELECTOR, ".bp-group-documents-meta")[0]
    dts = meta.find_elements(By.TAG_NAME, "dt")
    dds = meta.find_elements(By.TAG_NAME, "dd")
    details = meta.find_elements(By.CSS_SELECTOR, ".deposit-item-pub-metadata")
    if len(details) > 0:
        dts.extend(meta.find_elements(By.TAG_NAME, "dt"))
        dds.extend(meta.find_elements(By.TAG_NAME, "dd"))
    for dt, dd in zip(dts, dds):
        print(dd.text)
        if dt.text == "Metadata:":
            meta_desc_url = dd.find_elements(By.TAG_NAME, "a")[
                0
            ].get_attribute("href")
            meta_desc = get_desc_metadata(meta_desc_url)
        elif dt.text == "Published as:":
            metadata["published_as"] = dd.text
        else:
            metadata[dt.text.lower().replace(":", "").replace("(s)", "")] = (
                dd.text
            )

    filename = driver.find_element(
        By.CSS_SELECTOR, ".view_downloads > tbody > tr > td.value"
    )
    text = filename.text
    metadata["filename"] = text.strip()

    driver.quit()

    return {"visible_metadata": metadata, "page_xml_data": meta_desc}
