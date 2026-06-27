import argparse
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
    """
    Normalize whitespace.
    """

    if not text:
        return None

    return " ".join(text.split())


def get_page_soup(url):
    """
    Download page and return BeautifulSoup object.
    """

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.text,
        "lxml"
    )


def extract_title(soup):
    """
    Extract page title.
    """

    h1 = soup.find("h1")

    if h1:
        return clean_text(h1.get_text())

    return None


def extract_status(soup):
    """
    Detect Open / Closed.
    """

    page_text = soup.get_text(
        " ",
        strip=True
    ).lower()

    if "closed" in page_text:
        return "Closed"

    if "open" in page_text:
        return "Open"

    return None


def extract_all_sections(soup):
    """
    Extract all sections dynamically.

    Example:
    {
        "What do you get?": "...",
        "Who is this for?": "...",
        "Overview": "...",
        "Check if you can apply": "...",
        "How to apply": "..."
    }
    """

    sections = {}

    headings = soup.find_all(
        ["h2", "h3"]
    )

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
    """
    If page contains a section called
    'Check if you can apply'
    consider it eligible.
    """

    for section_name in sections:

        if "check if you can apply" in section_name.lower():
            return True

    return False


def crawl_grant(url):

    try:

        soup = get_page_soup(url)

        title = extract_title(soup)

        status = extract_status(soup)

        sections = extract_all_sections(soup)

        return {
            "url": url,
            "title": title,
            "status": status,
            "can_apply": extract_can_apply(sections),

            # Common fields
            "overview": sections.get("Overview"),
            "what_do_you_get": sections.get("What do you get?"),
            "who_is_this_for": sections.get("Who is this for?"),
            "check_if_you_can_apply": sections.get("Check if you can apply"),
            "how_to_apply": sections.get("How to apply")
        }

    except Exception as e:

        return {
            "url": url,
            "error": str(e)
        }


def main(input_file, output_file):

    with open(
        input_file,
        "r",
        encoding="utf-8"
    ) as f:

        grants = json.load(f)

    results = []

    total = len(grants)

    for index, grant in enumerate(grants, start=1):

        relative_link = grant.get("link")

        if not relative_link:
            continue

        full_url = urljoin(
            BASE_URL,
            relative_link
        )

        print(
            f"[{index}/{total}] Crawling: {full_url}"
        )

        details = crawl_grant(full_url)

        results.append({
            **grant,
            **details
        })

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\n✅ Saved {len(results)} grants "
        f"to {output_file}"
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
        default="output.json",
        help="Output file"
    )

    args = parser.parse_args()

    main(
        args.input_file,
        args.output
    )