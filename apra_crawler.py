# This module is responsible for the web crawling and data extraction logic
# for the APRA website.
# It will use the requests library to fetch web pages and BeautifulSoup
# to parse the HTML and extract relevant data.

import requests
from bs4 import BeautifulSoup
import re # For potential pillar detection
import time
import csv

# Module-level constant for the main URL
BANKING_HANDBOOK_URL = "https://handbook.apra.gov.au/industries/banking"

def get_standard_links(url: str) -> list[dict]:
    """
    Fetches the HTML content of the given URL, parses it using BeautifulSoup,
    and extracts links to individual standard pages, along with their category and pillar.

    Args:
        url: The URL of the page to crawl.

    Returns:
        A list of dictionaries, each containing 'url', 'category', and 'pillar'.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    collected_standards = []
    # Using a set to avoid duplicate URLs if they appear multiple times with same category/pillar
    seen_standards_info = set()


    # Define the titles of the main sections that will serve as categories
    section_titles = ["Governance", "Risk Management", "Financial Resilience", "Recovery and Resolution"]

    for category_name in section_titles:
        section_header = soup.find('h2', string=re.compile(r'\b' + re.escape(category_name) + r'\b', re.IGNORECASE))
        if section_header:
            pillar_name = None
            # Attempt to find pillar information near the header or in its text
            # This is a heuristic and highly dependent on HTML structure
            header_text_lower = section_header.get_text().lower()
            if "core" in header_text_lower:
                pillar_name = "Core"
            elif "supporting" in header_text_lower:
                pillar_name = "Supporting"

            # Look for links within a common parent of the header or a specific container
            # This might be a div containing the h2 and then the list of links
            # Or it could be the next sibling ul/div as before
            current_element = section_header
            quick_links_container = None
            # Try finding a common ancestor or a specific structure for links related to this section
            # This loop attempts to find a sibling 'ul' or 'div' that contains the links
            # It might need to go up to a parent and search downwards if the structure is complex
            for _ in range(3): # Check next few siblings
                if current_element:
                    current_element = current_element.find_next_sibling()
                    if current_element and current_element.name in ['ul', 'div']:
                        # Check if this container seems to hold the "quick links"
                        # This is a guess; may need class names or other attributes
                        if current_element.find('a', href=True): # If it has links
                            quick_links_container = current_element
                            break

            if not quick_links_container and section_header.parent.name in ['div', 'section']:
                 # Fallback: check within the parent of the header if it's a common container
                 quick_links_container = section_header.parent


            if quick_links_container:
                links = quick_links_container.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if not href.startswith('http'):
                        base_url = '/'.join(url.split('/')[:3])
                        href = base_url + href if href.startswith('/') else base_url + '/' + href

                    # Attempt to refine pillar based on link text if not found from header
                    link_text_lower = link.get_text().lower()
                    current_pillar = pillar_name
                    if not current_pillar: # If pillar wasn't found from section header
                        if "core" in link_text_lower:
                            current_pillar = "Core"
                        elif "supporting" in link_text_lower:
                            current_pillar = "Supporting"

                    standard_info_tuple = (href, category_name, current_pillar)
                    if standard_info_tuple not in seen_standards_info:
                        collected_standards.append({
                            "url": href,
                            "category": category_name,
                            "pillar": current_pillar
                        })
                        seen_standards_info.add(standard_info_tuple)
            else:
                print(f"Could not find 'Standards quick links' container for section: {category_name}")
        else:
            print(f"Could not find section: {category_name}")

    if not collected_standards:
        print("Specific sections not found or no links within them. Attempting a more generic link extraction.")
        content_divs = soup.find_all('div', class_=['content', 'main', 'body'])
        if not content_divs:
            content_divs = [soup.body]

        for div_idx, div in enumerate(content_divs):
            if div:
                links = div.find_all('a', href=True)
                for link_idx, link in enumerate(links):
                    href = link['href']
                    # Heuristic to filter relevant links
                    if any(keyword in href.lower() for keyword in ['standard', 'prudential', '.pdf', 'cps', 'sps', 'hps']):
                        if not href.startswith('http'):
                            base_url = '/'.join(url.split('/')[:3])
                            href = base_url + href if href.startswith('/') else base_url + '/' + href

                        # For fallback, category and pillar are unknown
                        standard_info_tuple = (href, None, None)
                        if standard_info_tuple not in seen_standards_info:
                            collected_standards.append({
                                "url": href,
                                "category": None,
                                "pillar": None
                            })
                            seen_standards_info.add(standard_info_tuple)

    if not collected_standards:
        print("No links found after attempting generic and fallback extraction.")

    return collected_standards


def extract_standard_details(standard_url: str, category: str | None, pillar: str | None) -> dict | None:
    """
    Fetches and parses a standard's page to extract details.

    Args:
        standard_url: The URL of the standard page.
        category: The category of the standard (e.g., "Governance").
        pillar: The pillar of the standard (e.g., "Core").

    Returns:
        A dictionary containing standard details, or None if fetching/parsing fails.
    """
    try:
        response = requests.get(standard_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching standard URL {standard_url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    details = {
        "title": None, # Extracted from page
        "url": standard_url, # Passed in
        "status": None, # Extracted from page
        "date": None, # Extracted from page
        "category": category, # Passed in
        "pillar": pillar # Passed in
    }

    # 1. Extract Title (usually in <h1>)
    title_tag = soup.find('h1')
    if title_tag:
        details["title"] = title_tag.get_text(strip=True)
    else:
        # Fallback: try to find a prominent title-like element
        title_tag_alt = soup.find('h2', class_=re.compile(r'title|heading', re.IGNORECASE))
        if title_tag_alt:
            details["title"] = title_tag_alt.get_text(strip=True)
        else:
            details["title"] = "Title not found" # Placeholder
            print(f"Could not find title (h1 or h2.title/heading) for {standard_url}")

    # 2. Extract Status and Date
    # Strategy: Look in common metadata areas, then more broadly.
    # Prioritize text closer to the title if possible.
    status_keywords = [
        "current", "final not yet in force", "effective", "commencement",
        "superseded", "revoked", "draft"
    ]
    # Regex for dates like "1 January 2024" or "01 Jan 2024" or "1 January 2008 – 30 September 2025"
    # It captures day, month, year, and an optional second date for ranges.
    date_pattern = re.compile(
        r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})"
        r"(?:\s*–\s*(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}))?",
        re.IGNORECASE
    )

    search_texts = []
    # Prefer specific metadata containers
    meta_containers = soup.find_all(['div', 'p', 'span'],
                                   class_=re.compile(r'meta|status|date|effective|publication', re.IGNORECASE))
    if meta_containers:
        for container in meta_containers:
            search_texts.append(container.get_text(separator=" ", strip=True))

    # If no specific containers, try text around H1 or in the header/article tags
    if not search_texts and title_tag:
        # Search siblings and parent of H1
        for sibling in title_tag.find_next_siblings(limit=5): # Check few elements after H1
             search_texts.append(sibling.get_text(separator=" ", strip=True))
        if title_tag.parent:
            search_texts.append(title_tag.parent.get_text(separator=" ", strip=True))

    if not search_texts: # Broad fallback if still nothing
        body_text = soup.body.get_text(separator=" ", strip=True)
        # Limit search to first N characters to avoid parsing huge irrelevant text blocks
        search_texts.append(body_text[:2000])


    found_status = None
    found_date = None

    for text_block in search_texts:
        if found_status and found_date:
            break # Already found both

        # Search for status
        if not found_status:
            for keyword in status_keywords:
                if keyword.lower() in text_block.lower(): # Case insensitive search for status
                    # Try to be more specific for "Current" to avoid matching "Currently"
                    if keyword == "current":
                         if re.search(r'\bcurrent\b', text_block, re.IGNORECASE):
                            found_status = "Current"
                            break
                    else:
                        found_status = keyword.capitalize() # e.g. "Final not yet in force"
                        break

        # Search for date
        if not found_date:
            match = date_pattern.search(text_block)
            if match:
                date_start = match.group(1)
                date_end = match.group(2)
                if date_end:
                    found_date = f"{date_start} – {date_end}"
                else:
                    found_date = date_start

    details["status"] = found_status
    details["date"] = found_date

    if not found_status:
        print(f"Status not found for {standard_url}")
    if not found_date:
        print(f"Date not found for {standard_url}")

    return details

# The old __main__ block that caused the SyntaxError has been removed.

def main():
    """
    Main function to run the APRA banking standards crawler and save data to CSV.
    """
    # BANKING_HANDBOOK_URL is now a global constant, no longer defined here.

    print(f"Starting APRA Banking Standards Crawler for URL: {BANKING_HANDBOOK_URL}")

    standard_links_with_meta = get_standard_links(BANKING_HANDBOOK_URL) # Uses the global constant
    all_standards_data = []

    if not standard_links_with_meta:
        print("No standard links found. Exiting.")
    else:
        print(f"Found {len(standard_links_with_meta)} standard links to process.")
        for idx, standard_item in enumerate(standard_links_with_meta):
            url = standard_item.get('url')
            category = standard_item.get('category')
            pillar = standard_item.get('pillar')

            if not url:
                print(f"Skipping item with missing URL: {standard_item}")
                continue

            print(f"Processing ({idx+1}/{len(standard_links_with_meta)}): {url}...")

            time.sleep(0.5) # Be polite

            details = extract_standard_details(url, category, pillar)

            if details:
                all_standards_data.append(details)
            else:
                print(f"Failed to extract details for {url} (network error or critical parse failure).")

        if all_standards_data:
            output_csv_file = "apra_banking_standards.csv"
            fieldnames = ["title", "url", "status", "date", "category", "pillar"]

            print(f"\nWriting {len(all_standards_data)} extracted standard details to {output_csv_file}...")

            try:
                with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_standards_data)
                print(f"Successfully saved data to {output_csv_file}")
            except IOError as e:
                print(f"Error writing CSV file: {e}")
        else:
            print("\nNo data was successfully extracted from any standard page.")
            if standard_links_with_meta:
                print("This might be due to issues with parsing individual standard pages or all pages returned errors.")

    print("Crawler finished.")
    # Optionally return data for other programmatic uses, though __main__ doesn't use it.
    return all_standards_data

# This was the end of the main() function.
# The if __name__ == "__main__": block should follow directly.

if __name__ == "__main__":
    # Ensure csv and time are imported if main() relies on them being in global scope
    # and not passed as arguments or imported within main().
    # Top-level imports of csv and time are already present in this file.
    main()
