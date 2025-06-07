# This module is responsible for the web crawling and data extraction logic
# for the APRA website.
# It will use the requests library to fetch web pages and BeautifulSoup
# to parse the HTML and extract relevant data.

import requests
from bs4 import BeautifulSoup
import re # For potential pillar detection
import time
import csv
import markdownify
import os

# Module-level constant for the main URL
BANKING_HANDBOOK_URL = "https://handbook.apra.gov.au/industries/banking"

def create_output_directory(dir_name: str = "output/markdown_standards"):
    """Creates the output directory if it doesn't exist."""
    os.makedirs(dir_name, exist_ok=True)
    print(f"Ensured output directory exists: {dir_name}")

def sanitize_filename(filename: str) -> str:
    """Removes/replaces characters that are invalid for filenames."""
    if not filename:
        return "untitled_standard"

    # Replace non-breaking spaces (and other common problematic whitespace) with a regular space
    filename = filename.replace('\xa0', ' ') # Non-breaking space
    filename = filename.replace('\u200B', ' ') # Zero-width space

    # Replace typographic quotes/apostrophes with underscore
    filename = filename.replace('\u2018', '_') # Left single quotation mark
    filename = filename.replace('\u2019', '_') # Right single quotation mark (apostrophe)
    filename = filename.replace('\u201C', '_') # Left double quotation mark
    filename = filename.replace('\u201D', '_') # Right double quotation mark
    # Add more replacements here if other specific problematic unicode chars are found

    # Remove or replace invalid OS path characters: / \ : * ? " < > |
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Replace multiple spaces (resulting from above or originally) with a single underscore
    filename = re.sub(r'\s+', '_', filename.strip())

    # Optional: further restrict to a more limited set of characters for extreme safety
    # filename = re.sub(r'[^a-zA-Z0-9_.-]', '', filename)

    # Replace spaces (now underscores) with underscores - this is redundant if re.sub(r'\s+', '_', ...) is used
    # filename = filename.replace(' ', '_') # Already handled by \s+
    # Limit length (optional, but good practice)
    return filename[:150]


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

    # Find all H2 elements, assuming they are category headers
    category_headers = soup.find_all('h2')

    if not category_headers:
        print("No H2 category headers found. Proceeding to generic fallback.")

    for section_header in category_headers:
        category_name = section_header.get_text(strip=True)
        # Basic filter for relevant category names if needed, e.g., checking against a known list
        # For now, assume all H2s are relevant categories if they have subsequent links

        print(f"Processing category: {category_name}")

        # Iterate through siblings of the H2 to find sub-groups (pillar containers) and link lists
        current_pillar = None # Reset pillar for each new H2 section

        for sibling in section_header.find_next_siblings():
            if sibling.name == 'h2': # Stop if we hit the next category header
                break

            # Check if this sibling defines a pillar (e.g., H3 or button)
            potential_pillar_element = None
            if sibling.name in ['h3', 'button']:
                potential_pillar_element = sibling
            elif sibling.name in ['div', 'section']: # Check for h3/button within a wrapper div
                potential_pillar_element = sibling.find(['h3', 'button'])

            if potential_pillar_element:
                pillar_text = potential_pillar_element.get_text().lower()
                if "core" in pillar_text:
                    current_pillar = "Core"
                elif "supporting" in pillar_text:
                    current_pillar = "Supporting"
                # If a pillar is set, it applies to subsequent link lists within this sibling group.
                # If an element is both a pillar definer AND a link container, this works.
                # If pillar definer is separate from link container, the pillar context is now set.

            # Look for link containers (ul, or div that might be a "quick links" group)
            # This can be the sibling itself, or nested within the sibling.
            link_containers_to_check = []
            if sibling.name in ['ul', 'div']: # Common for quick links
                link_containers_to_check.append(sibling)
            # Also check within the sibling if it's a general div/section wrapper
            if sibling.name in ['div', 'section']:
                 link_containers_to_check.extend(sibling.find_all(['ul', 'div']))


            found_links_in_sibling_group = False
            for container in link_containers_to_check:
                # Heuristic: a link container is more likely if it has multiple 'li > a' or directly 'a'
                # This is a guess, may need class names like 'quick-links' from actual site
                links = container.find_all('a', href=True)
                if not links:
                    continue

                # Check if it looks like a list of standards (e.g., has 'li' children if 'ul')
                # Or if it's a div, does it seem to be a "quick links" group?
                # This heuristic might need refinement based on actual page structure.
                # For now, if we find links directly in a ul/div sibling or nested, process them.

                for link_tag in links:
                    href = link_tag['href']
                    if not href or href.startswith('#'): # Skip empty or anchor links
                        continue

                    if not href.startswith('http'):
                        base_url = '/'.join(url.split('/')[:3])
                        href = base_url + href if href.startswith('/') else base_url + '/' + href

                    # Pillar determination:
                    # 1. Use current_pillar if set by h3/button sibling.
                    # 2. Fallback: check link text itself (as in previous version)
                    final_pillar = current_pillar
                    if not final_pillar:
                        link_text_lower = link_tag.get_text().lower()
                        if "core" in link_text_lower:
                            final_pillar = "Core"
                        elif "supporting" in link_text_lower:
                            final_pillar = "Supporting"

                    standard_info_tuple = (href, category_name, final_pillar)
                    if standard_info_tuple not in seen_standards_info:
                        collected_standards.append({
                            "url": href,
                            "category": category_name,
                            "pillar": final_pillar
                        })
                        seen_standards_info.add(standard_info_tuple)
                        found_links_in_sibling_group = True

                if found_links_in_sibling_group and container.name == 'ul': # Often, a UL is the definitive list.
                    break # Processed this UL, move to next sibling of H2.

            # If links were found and processed, and a pillar was identified from an h3/button,
            # subsequent link groups under the same H2 might not have their own h3/button pillar.
            # The current_pillar context should ideally persist until a new pillar-defining element or new H2.
            # However, if the structure is flat (H2 -> UL, H2 -> H3 -> UL), current_pillar resets too broadly.
            # For now, current_pillar is reset for each sibling of H2 unless that sibling itself sets it.
            # This might need more advanced state if a pillar applies across multiple sibling elements.
            # The current logic: pillar is set if h3/button is found in *this* sibling or its children.
            # If the next sibling is another list of links without an h3/button, current_pillar might be None again.
            # This is a simplification; true structure might require passing pillar context down differently.


    if not collected_standards: # Fallback if the structured H2 -> siblings search yields nothing
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


def extract_standard_details(standard_url: str, category: str | None, pillar: str | None) -> tuple[dict | None, BeautifulSoup | None]:
    """
    Fetches and parses a standard's page to extract details and the parsed soup object.

    Args:
        standard_url: The URL of the standard page.
        category: The category of the standard (e.g., "Governance").
        pillar: The pillar of the standard (e.g., "Core").

    Returns:
        A tuple containing (details_dictionary, soup_object), or (None, None) if fetching/parsing fails.
    """
    try:
        response = requests.get(standard_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching standard URL {standard_url}: {e}")
        return None, None

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
    date_pattern = re.compile(
        r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})"
        r"(?:\s*–\s*(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}))?",
        re.IGNORECASE
    )

    found_status = None
    found_date = None

    # Primary Strategy for Status and Date: Vicinity of Title
    if title_tag:
        search_area = title_tag.parent # Search within the parent container of the title
        if search_area:
            # Look for ul, or sequences of p/div that might contain status/date
            potential_meta_holders = search_area.find_all(['ul', 'div', 'p'], recursive=False, limit=10)
            if not potential_meta_holders and title_tag: # If title is not wrapped check its direct siblings
                 potential_meta_holders = title_tag.find_next_siblings(limit=5)

            for i, el_container in enumerate(potential_meta_holders):
                # Get text with spaces to ensure word boundaries
                container_text_for_status_search = el_container.get_text(separator=' ', strip=True)
                container_text_lower_for_status = container_text_for_status_search.lower()

                if not found_status:
                    for keyword in status_keywords:
                        if keyword == "current" and re.search(r'\bcurrent\b', container_text_lower_for_status):
                            found_status = "Current"
                            break
                        elif keyword != "current" and keyword in container_text_lower_for_status:
                            found_status = keyword.capitalize()
                            break

                if found_status and not found_date: # Status found, now look for date in this or next element
                    # Check current element's full text (with separator) for date
                    date_match = date_pattern.search(container_text_for_status_search)
                    if date_match:
                        ds, de = date_match.group(1), date_match.group(2)
                        found_date = f"{ds} – {de}" if de else ds
                        # If status and date are found in the same container, break from iterating potential_meta_holders
                        if found_status and found_date:
                            break

                    # If date not in the same container text as status, check next element (if any)
                    # This part of the logic might be too complex if status is in one <p> and date in next <p>
                    # The current loop iterates through *containers* (like a whole div.metadata or a ul).
                    # A better approach for p, p, p sequences:
                    # Iterate through individual <p> tags if el_container is a div.

                    # Simplified: if date not in the combined text of the current meta_holder,
                    # and if the next meta_holder is very close and seems related, check it.
                    # However, the current loop structure processes one meta_holder at a time.
                    # The original logic of checking el and then next_el was for a flat list of <p>s.
                    # If el_container is a div, date should be within its text.
                    # If el_container is a <p> that has status, and next <p> has date:
                    if not found_date and i + 1 < len(potential_meta_holders):
                        # This assumes potential_meta_holders is a list of <p> tags primarily
                        next_el_text_for_date = potential_meta_holders[i+1].get_text(strip=True)
                        date_match_next = date_pattern.search(next_el_text_for_date)
                        if date_match_next:
                            ds, de = date_match_next.group(1), date_match_next.group(2)
                            found_date = f"{ds} – {de}" if de else ds
                            # Break from iterating potential_meta_holders
                            if found_status and found_date:
                                 break
                if found_status and found_date:
                    break
            if found_status and found_date: # break outer loop if both found
                 pass # proceed to assign to details

    # Fallback Strategy for Status and Date (if primary failed)
    if not found_status or not found_date:
        print(f"Primary status/date search failed for {standard_url}. Using fallback.")
        search_texts_fallback = []
        meta_containers = soup.find_all(['div', 'p', 'span'],
                                       class_=re.compile(r'meta|status|date|effective|publication', re.IGNORECASE))
        if meta_containers:
            for container in meta_containers:
                search_texts_fallback.append(container.get_text(separator=" ", strip=True))

        if not search_texts_fallback: # Broader fallback
            if soup.body: # Check if soup.body is not None
                body_text = soup.body.get_text(separator=" ", strip=True)
                search_texts_fallback.append(body_text[:2000]) # Limit search space
            else:
                print(f"Warning: No soup.body found for {standard_url}. Skipping body text search for status/date.")

        for text_block in search_texts_fallback:
            if not found_status:
                for keyword in status_keywords:
                    if keyword == "current" and re.search(r'\bcurrent\b', text_block, re.IGNORECASE):
                        found_status = "Current"; break
                    elif keyword != "current" and keyword.lower() in text_block.lower():
                        found_status = keyword.capitalize(); break

            if not found_date:
                match = date_pattern.search(text_block)
                if match:
                    ds, de = match.group(1), match.group(2)
                    found_date = f"{ds} – {de}" if de else ds

            if found_status and found_date: break

    details["status"] = found_status
    details["date"] = found_date

    # Category and Pillar Extraction (Fallback/Augmentation)
    if details["category"] is None or details["pillar"] is None:
        print(f"Attempting to find category/pillar on page for {standard_url}")
        framework_header = soup.find(['h2', 'h3'], string=re.compile(r'Prudential framework pillar', re.IGNORECASE))
        if framework_header:
            current_element = framework_header.find_next_sibling()
            framework_items_texts = []
            # Look for a list (ul) or a few subsequent p/div tags
            if current_element and current_element.name == 'ul':
                for li in current_element.find_all('li', limit=3): # Max 3 items for cat/sub-cat/pillar
                    framework_items_texts.append(li.get_text(strip=True))
            elif current_element: # Check a few p/div tags
                count = 0
                while current_element and current_element.name in ['p', 'div'] and count < 3:
                    framework_items_texts.append(current_element.get_text(strip=True))
                    current_element = current_element.find_next_sibling()
                    count +=1

            if framework_items_texts:
                if details["category"] is None and len(framework_items_texts) > 0:
                    # Assuming first item is category if not already set
                    details["category"] = framework_items_texts[0]

                if details["pillar"] is None:
                    for item_text in framework_items_texts: # Check all found items for pillar keyword
                        item_text_lower = item_text.lower()
                        if "core" in item_text_lower:
                            details["pillar"] = "Core"
                            break
                        elif "supporting" in item_text_lower:
                            details["pillar"] = "Supporting"
                            break

    if not found_status: print(f"Status not found for {standard_url}")
    if not found_date: print(f"Date not found for {standard_url}")
    if details["category"] is None: print(f"Category not found for {standard_url}")
    if details["pillar"] is None: print(f"Pillar not found for {standard_url}")

    return details, soup

# The old __main__ block that caused the SyntaxError has been removed.

def main():
    """
    Main function to run the APRA banking standards crawler and save data to CSV and Markdown.
    """
    create_output_directory() # Create markdown output directory
    markdown_dir = "output/markdown_standards"

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

            details, soup = extract_standard_details(url, category, pillar)

            if details and soup:
                all_standards_data.append(details)

                # Isolate Main Content for Markdown
                main_content_element = None
                # Try specific selectors first
                # Based on APRA handbook structure, a div with id="document-content" or class="document-content" seems likely
                selectors_to_try = [
                    soup.find('div', id='document-content'),
                    soup.find('div', class_='document-content'),
                    soup.find('article'),
                    soup.find('div', id='content'),
                    soup.find('div', id='main-content'),
                    soup.find('div', class_='page-content'),
                    soup.find('div', class_='entry-content'),
                    soup.find('div', class_='content-area'),
                    soup.find('div', class_='region-content'), # From original prompt
                ]
                for el in selectors_to_try:
                    if el:
                        main_content_element = el
                        break

                if main_content_element:
                    main_content_html = str(main_content_element)
                    markdown_content = convert_html_to_markdown(main_content_html)

                    title_for_filename = details.get('title', 'untitled_standard')
                    if not title_for_filename or title_for_filename == "Title not found":
                        # Use part of URL or a placeholder if title is bad
                        placeholder_name = url.split('/')[-1] or url.split('/')[-2] or "unknown_standard"
                        title_for_filename = sanitize_filename(placeholder_name) if placeholder_name else "untitled_standard"

                    safe_filename = sanitize_filename(title_for_filename)
                    markdown_filepath = os.path.join(markdown_dir, safe_filename + ".md")

                    try:
                        with open(markdown_filepath, 'w', encoding='utf-8') as md_file:
                            md_file.write(markdown_content)
                        print(f"Saved Markdown for '{title_for_filename}' to {markdown_filepath}")
                    except IOError as e:
                        print(f"Error writing Markdown file {markdown_filepath}: {e}")
                else:
                    print(f"Warning: Main content area not identified for {url}. Skipping Markdown generation.")
            elif details: # Details found but no soup object (shouldn't happen with current logic)
                 all_standards_data.append(details)
                 print(f"Warning: Details found but no soup object for {url}. Skipping Markdown generation.")
            else:
                print(f"Failed to extract details and soup for {url} (network error or critical parse failure).")

        if all_standards_data:
            output_csv_file = "apra_banking_standards.csv" # CSV still goes to root
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

def convert_html_to_markdown(html_content: str) -> str:
    """Converts a string of HTML content to Markdown."""
    return markdownify.markdownify(html_content)

if __name__ == "__main__":
    # Ensure csv and time are imported if main() relies on them being in global scope
    # and not passed as arguments or imported within main().
    # Top-level imports of csv and time are already present in this file.
    main()
