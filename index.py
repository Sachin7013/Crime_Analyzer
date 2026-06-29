import argparse
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

BASE_URL = "https://business.gov.au"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}


def clean_text(text):
    if not text:
        return None
    return " ".join(text.split())


def strip_html(html_string):
    if not html_string:
        return None
    soup = BeautifulSoup(html_string, "lxml")
    return clean_text(soup.get_text(" ", strip=True))


def timestamp_to_date(ts):
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
    except (ValueError, OSError, TypeError):
        return None


def get_page_soup(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def extract_title(soup):
    h1 = soup.find("h1")
    if h1:
        return clean_text(h1.get_text())
    return None


def extract_status(soup):
    page_text = soup.get_text(" ", strip=True).lower()
    if "closed" in page_text:
        return "Closed"
    if "open" in page_text:
        return "Open"
    return None


def extract_all_sections(soup):
    sections = {}
    headings = soup.find_all(["h2", "h3"])

    for heading in headings:
        section_title = clean_text(
            heading.get_text(" ", strip=True)
        )
        content = []
        current = heading.find_next_sibling()

        while current:
            if current.name in ["h2", "h3"]:
                break
            text = clean_text(
                current.get_text(" ", strip=True)
            )
            if text:
                content.append(text)
            current = current.find_next_sibling()

        if content:
            sections[section_title] = "\n".join(content)

    return sections


def extract_can_apply(sections):
    for section_name in sections:
        if "check if you can apply" in section_name.lower():
            return True
    return False


def extract_grant_metadata(result):
    raw = result.get("raw", {})

    return {
        "title": result.get("title") or raw.get("ctitle"),
        "status": raw.get("cgs"),
        "closeDate": timestamp_to_date(raw.get("closez32xdate")),
        "startDate": timestamp_to_date(raw.get("startz32xdate")),
        "description": raw.get("csearchcarddescription"),
        "short_description": raw.get("fshortz32xdescription28333"),
        "heading": raw.get("fheading28333"),
        "what_do_you_get_raw": strip_html(raw.get("whatz32xyouz32xget")),
        "who_is_this_for_raw": strip_html(raw.get("whoz32xthisz32xisz32xfor")),
        "contact_phone": raw.get("ccontactphone"),
        "relative_url": raw.get("curl"),
        "click_uri": result.get("clickUri"),
    }


def crawl_grant(url):
    try:
        soup = get_page_soup(url)
        title = extract_title(soup)
        status = extract_status(soup)
        sections = extract_all_sections(soup)

        return {
            "crawled_title": title,
            "crawled_status": status,
            "can_apply": extract_can_apply(sections),
            "overview": sections.get("Overview"),
            "what_do_you_get": sections.get("What do you get?"),
            "who_is_this_for": sections.get("Who is this for?"),
            "check_if_you_can_apply": sections.get(
                "Check if you can apply"
            ),
            "how_to_apply": sections.get("How to apply"),
            "all_sections": sections,
            "crawl_error": None,
        }

    except Exception as e:
        return {"crawl_error": str(e)}


def process_coveo_results(grants):
    results = []
    total = len(grants)

    for index, grant in enumerate(grants, start=1):
        metadata = extract_grant_metadata(grant)

        relative_url = metadata.get("relative_url")
        if not relative_url:
            print(
                f"[{index}/{total}] Skipping "
                f"(no URL): {metadata.get('title')}"
            )
            continue

        full_url = urljoin(BASE_URL, relative_url)
        print(f"[{index}/{total}] Crawling: {full_url}")

        crawled = crawl_grant(full_url)

        result = {
            "title": metadata["title"],
            "url": full_url,
            "status": (
                crawled.get("crawled_status")
                or metadata["status"]
            ),
            "closeDate": metadata["closeDate"],
            "startDate": metadata["startDate"],
            "description": metadata["description"],
            "contact_phone": metadata["contact_phone"],
            "can_apply": crawled.get("can_apply", False),
            "overview": crawled.get("overview"),
            "what_do_you_get": (
                crawled.get("what_do_you_get")
                or metadata["what_do_you_get_raw"]
            ),
            "who_is_this_for": (
                crawled.get("who_is_this_for")
                or metadata["who_is_this_for_raw"]
            ),
            "check_if_you_can_apply": crawled.get(
                "check_if_you_can_apply"
            ),
            "how_to_apply": crawled.get("how_to_apply"),
            "all_sections": crawled.get("all_sections", {}),
            "crawl_error": crawled.get("crawl_error"),
        }

        results.append(result)

    return results


def process_old_format(grants):
    results = []
    total = len(grants)

    for index, grant in enumerate(grants, start=1):
        relative_link = grant.get("link")
        if not relative_link:
            continue

        full_url = urljoin(BASE_URL, relative_link)
        print(f"[{index}/{total}] Crawling: {full_url}")

        details = crawl_grant(full_url)
        results.append({**grant, **details})

    return results


def main(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "results" in data:
        grants = data["results"]
        total_available = data.get("totalCount", len(grants))
        print(
            f"Coveo API response: {len(grants)} results "
            f"loaded (total available: {total_available})"
        )
        results = process_coveo_results(grants)
    elif isinstance(data, list):
        print(f"Legacy format: {len(data)} grants loaded")
        results = process_old_format(data)
    else:
        print("Error: Unrecognized JSON structure")
        return

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(
        f"\nSaved {len(results)} grants to {output_file}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Business.gov.au Grant Crawler"
    )

    parser.add_argument(
        "input_file",
        help="Input grants JSON file"
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file (defaults to output_YYYYMMDD_HHMMSS.json)"
    )

    args = parser.parse_args()

    output_file = args.output
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output_{timestamp}.json"

    main(args.input_file, output_file)
