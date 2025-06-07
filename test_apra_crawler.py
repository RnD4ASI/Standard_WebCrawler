import unittest
from unittest.mock import patch, MagicMock, mock_open
import io
import csv
import os # Added import for os.path.join

# Assuming apra_crawler.py is in the same directory or accessible in PYTHONPATH
import apra_crawler

class TestGetStandardLinks(unittest.TestCase):
    @patch('apra_crawler.requests.get')
    def test_get_standard_links_happy_path(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = """
        <html><body>
            <h2>Governance</h2>
            <div>
                <p>Some text about Governance Core</p>
                <ul> <!-- Simulating "Standards quick links" -->
                    <li><a href="/standards/cps-101">CPS 101 Governance Core</a></li>
                    <li><a href="/standards/sps-102">SPS 102 Supporting</a></li>
                </ul>
            </div>
            <h2>Risk Management</h2>
            <div>
                 <p>Some text about Risk Management Supporting</p>
                 <div> <!-- Simulating "Standards quick links" container -->
                    <a href="https://example.com/standards/cps-201">CPS 201 Risk Core</a>
                 </div>
            </div>
            <h2>Financial Resilience</h2>
            <!-- No links here -->
            <h2>Recovery and Resolution</h2>
            <!-- No specific container, link is just there -->
            <a href="/other/rps303.pdf">RPS 303 PDF Standard</a>
        </body></html>
        """
        mock_requests_get.return_value = mock_response

        base_url_for_test = "https://handbook.apra.gov.au" # Example, matches get_standard_links logic
        expected_links = [
            {'url': base_url_for_test + '/standards/cps-101', 'category': 'Governance', 'pillar': 'Core'},
            {'url': base_url_for_test + '/standards/sps-102', 'category': 'Governance', 'pillar': 'Supporting'},
            {'url': 'https://example.com/standards/cps-201', 'category': 'Risk Management', 'pillar': 'Core'},
            # Note: rps303.pdf might be picked up by fallback if section logic is strict, or by section if less strict.
            # Based on current get_standard_links, it's likely not picked by section logic if not in a list/div after h2.
            # Let's assume the fallback picks it if section logic fails for "Recovery and Resolution"
        ]

        result = apra_crawler.get_standard_links(base_url_for_test + "/industries/banking")

        # Comparing lists of dicts can be tricky if order changes. Sort or use set comparisons.
        # For simplicity, we'll check if all expected items are in results, and length.
        self.assertEqual(len(result), 3) # cps-101, sps-102, cps-201. rps303 won't be found by section logic.
        for expected_item in expected_links[:3]: # only check the first 3 that should be found by section logic
            self.assertIn(expected_item, result)


    @patch('apra_crawler.requests.get')
    def test_get_standard_links_fallback_no_sections(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Ensure this HTML is exactly what's processed
        mock_response.content = """
        <html><body>
            <p>Some introductory text.</p>
            <a href="/standards/cps-510.html">CPS 510 Standard</a>
            <a href="another-standard.pdf">Another Standard PDF</a>
            <a href="/irrelevant-topic">Irrelevant link</a>
            <a href="https://example.com/page/sps-220">SPS 220 Prudential Standard</a>
        </body></html>
        """
        mock_requests_get.return_value = mock_response

        base_url_for_test = "https://handbook.apra.gov.au"
        expected_links = [
            {'url': base_url_for_test + '/standards/cps-510.html', 'category': None, 'pillar': None},
            {'url': base_url_for_test + '/another-standard.pdf', 'category': None, 'pillar': None},
            {'url': 'https://example.com/page/sps-220', 'category': None, 'pillar': None},
        ]

        result = apra_crawler.get_standard_links(base_url_for_test + "/industries/banking")

        self.assertEqual(len(result), len(expected_links))
        for item in expected_links:
            self.assertIn(item, result)

    # The erroneously indented block has been removed.
    # The next test 'test_get_standard_links_network_error' should follow directly.
    @patch('apra_crawler.requests.get')
    def test_get_standard_links_network_error(self, mock_requests_get):
        mock_requests_get.side_effect = apra_crawler.requests.exceptions.RequestException("Test network error")

        result = apra_crawler.get_standard_links("https://handbook.apra.gov.au/industries/banking")
        self.assertEqual(result, [])

    @patch('apra_crawler.requests.get')
    def test_get_standard_links_empty_page(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = "<html><body></body></html>"
        mock_requests_get.return_value = mock_response

        result = apra_crawler.get_standard_links("https://handbook.apra.gov.au/industries/banking")
        # Expect fallback to kick in, find no relevant links, and return empty list.
        self.assertEqual(result, [])


class TestExtractStandardDetails(unittest.TestCase):
    @patch('apra_crawler.requests.get')
    def test_extract_details_happy_path_current(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = """
        <html><body>
            <h1>CPS 510 Governance</h1>
            <div class="metadata">
                <p>Status: Current</p>
                <p>Effective Date: 1 January 2024</p>
            </div>
        </body></html>
        """
        mock_requests_get.return_value = mock_response

        url = "https://example.com/cps-510"
        category = "Governance"
        pillar = "Core"
        expected_details = {
            "title": "CPS 510 Governance",
            "url": url,
            "status": "Current", # Based on "Current" keyword
            "date": "1 January 2024",
            "category": category,
            "pillar": pillar
        }

        result_dict, result_soup = apra_crawler.extract_standard_details(url, category, pillar)
        self.assertEqual(result_dict, expected_details)
        self.assertIsNotNone(result_soup) # Basic check that soup is returned

    @patch('apra_crawler.requests.get')
    def test_extract_details_final_not_in_force_range(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = """
        <html><body>
            <header><h1>SPS 250 Insurance</h1></header>
            <div class="content-meta">
                Final not yet in force. Commencement: 1 July 2025 – 30 June 2026
            </div>
        </body></html>
        """
        mock_requests_get.return_value = mock_response

        url = "https://example.com/sps-250"
        category = "Insurance Risk" # Example
        pillar = "Supporting"
        expected_details = {
            "title": "SPS 250 Insurance",
            "url": url,
            "status": "Final not yet in force",
            "date": "1 July 2025 – 30 June 2026",
            "category": category,
            "pillar": pillar
        }

        result_dict, result_soup = apra_crawler.extract_standard_details(url, category, pillar)
        self.assertEqual(result_dict, expected_details)
        self.assertIsNotNone(result_soup)

    @patch('apra_crawler.requests.get')
    def test_extract_details_missing_info(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = """
        <html><body>
            <!-- No H1 title -->
            <div class="some-status-area">
                <p>Status: Current</p>
                <!-- No date here -->
            </div>
        </body></html>
        """
        mock_requests_get.return_value = mock_response

        url = "https://example.com/cps-999"
        category = "Other"
        pillar = None
        expected_details = {
            "title": "Title not found", # Placeholder from implementation
            "url": url,
            "status": "Current",
            "date": None, # Date is missing in HTML
            "category": category,
            "pillar": pillar
        }

        result_dict, result_soup = apra_crawler.extract_standard_details(url, category, pillar)
        self.assertEqual(result_dict, expected_details)
        self.assertIsNotNone(result_soup)


    @patch('apra_crawler.requests.get')
    def test_extract_details_network_error(self, mock_requests_get):
        mock_requests_get.side_effect = apra_crawler.requests.exceptions.RequestException("Test network error")

        result_dict, result_soup = apra_crawler.extract_standard_details("https://example.com/error-page", "ErrorCategory", "ErrorPillar")
        self.assertIsNone(result_dict)
        self.assertIsNone(result_soup)

class TestMainScript(unittest.TestCase):
    # Patch target is 'apra_crawler.get_standard_links' because main() in apra_crawler.py will call it from its own module.
    @patch('apra_crawler.create_output_directory') # Mock directory creation
    @patch('apra_crawler.get_standard_links')
    @patch('apra_crawler.extract_standard_details')
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictWriter')
    @patch('apra_crawler.convert_html_to_markdown') # Mock markdown conversion
    # Note: The order of mock arguments to the test function is from bottom-up for decorators.
    def test_main_logic_with_data_and_csv_writing(self, mock_convert_to_markdown, mock_csv_dict_writer, mock_builtin_open, mock_extract_details, mock_get_links, mock_create_dir):
        # 1. Setup Mocks
        mock_get_links.return_value = [
            {'url': 'http://example.com/cps101', 'category': 'Governance', 'pillar': 'Core'},
            {'url': 'http://example.com/sps202', 'category': 'Risk', 'pillar': 'Supporting'}
        ]

        # Mock soup object needed for main() logic
        mock_soup_cps101 = MagicMock(spec=apra_crawler.BeautifulSoup)
        mock_soup_sps202 = MagicMock(spec=apra_crawler.BeautifulSoup)

        # Simulate finding a main content element
        mock_main_content_element_cps101 = MagicMock()
        mock_main_content_element_cps101.__str__.return_value = "<html><body><h1>CPS 101 Content</h1></body></html>"
        mock_soup_cps101.find.return_value = mock_main_content_element_cps101

        mock_main_content_element_sps202 = MagicMock()
        mock_main_content_element_sps202.__str__.return_value = "<html><body><h1>SPS 202 Content</h1></body></html>"
        mock_soup_sps202.find.return_value = mock_main_content_element_sps202

        details_cps101 = {'title': 'CPS 101 Governance', 'url': 'http://example.com/cps101', 'status': 'Current', 'date': 'Jan 2023', 'category': 'Governance', 'pillar': 'Core'}
        details_sps202 = {'title': 'SPS 202 Risk Mgt', 'url': 'http://example.com/sps202', 'status': 'Draft', 'date': 'Feb 2024', 'category': 'Risk', 'pillar': 'Supporting'}

        mock_extract_details.side_effect = [
            (details_cps101, mock_soup_cps101),
            (details_sps202, mock_soup_sps202)
        ]

        mock_convert_to_markdown.side_effect = ["CPS 101 Markdown", "SPS 202 Markdown"]

        mock_writer_instance = MagicMock()
        mock_csv_dict_writer.return_value = mock_writer_instance

        # Create specific MagicMock instances for each file handle
        mock_csv_file_handle = MagicMock(name="csv_file_handle")
        mock_md_file_handle1 = MagicMock(name="md_file_handle1")
        mock_md_file_handle2 = MagicMock(name="md_file_handle2")

        # Corrected order: MD1, MD2, then CSV
        mock_builtin_open.side_effect = [mock_md_file_handle1, mock_md_file_handle2, mock_csv_file_handle]


        # 2. Call the main function from apra_crawler
        # The BANKING_HANDBOOK_URL is hardcoded in apra_crawler.main, so we don't need to pass it.
        # The output_csv_file is also hardcoded.
        returned_data = apra_crawler.main()

        # 3. Assertions
        # BANKING_HANDBOOK_URL is used by apra_crawler.main() internally
        mock_get_links.assert_called_once_with(apra_crawler.BANKING_HANDBOOK_URL)
        self.assertEqual(mock_extract_details.call_count, 2)
        # ... existing assertions for extract_details calls ...

        # Check that the data returned by main() is what we expect (list of dicts)
        self.assertEqual(returned_data, [details_cps101, details_sps202])

        # Check CSV writing
        mock_builtin_open.assert_any_call("apra_banking_standards.csv", 'w', newline='', encoding='utf-8')
        # The object passed to DictWriter should be the result of mock_csv_file_handle.__enter__()
        mock_csv_dict_writer.assert_called_once_with(mock_csv_file_handle.__enter__(), fieldnames=["title", "url", "status", "date", "category", "pillar"])
        mock_writer_instance.writeheader.assert_called_once() # This is called on the DictWriter instance
        # writerows is also called on the DictWriter instance, which is mock_writer_instance
        mock_writer_instance.writerows.assert_called_once_with([details_cps101, details_sps202])

        # Check Markdown saving
        mock_create_dir.assert_called_once()
        self.assertEqual(mock_convert_to_markdown.call_count, 2)
        mock_convert_to_markdown.assert_any_call("<html><body><h1>CPS 101 Content</h1></body></html>")
        mock_convert_to_markdown.assert_any_call("<html><body><h1>SPS 202 Content</h1></body></html>")

        # Check that open was called for markdown files
        sanitized_title_cps101 = apra_crawler.sanitize_filename(details_cps101['title'])
        sanitized_title_sps202 = apra_crawler.sanitize_filename(details_sps202['title'])

        expected_md_path_cps101 = os.path.join("output/markdown_standards", sanitized_title_cps101 + ".md")
        expected_md_path_sps202 = os.path.join("output/markdown_standards", sanitized_title_sps202 + ".md")

        # Check calls to open for MD files (these are the others in mock_builtin_open.side_effect)
        mock_builtin_open.assert_any_call(expected_md_path_cps101, 'w', encoding='utf-8')
        mock_builtin_open.assert_any_call(expected_md_path_sps202, 'w', encoding='utf-8')

        # Check that write was called on the MD file handles' __enter__() result
        mock_md_file_handle1.__enter__().write.assert_called_once_with("CPS 101 Markdown")
        mock_md_file_handle2.__enter__().write.assert_called_once_with("SPS 202 Markdown")


    @patch('apra_crawler.create_output_directory')
    @patch('apra_crawler.get_standard_links')
    @patch('apra_crawler.extract_standard_details')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_logic_no_links_found(self, mock_builtin_open, mock_extract_details, mock_get_links, mock_create_dir):
        mock_get_links.return_value = [] # No links found

        apra_crawler.main()

        mock_create_dir.assert_called_once()
        mock_get_links.assert_called_once_with(apra_crawler.BANKING_HANDBOOK_URL)
        mock_extract_details.assert_not_called()
        mock_builtin_open.assert_not_called() # CSV file should not be opened

    @patch('apra_crawler.create_output_directory')
    @patch('apra_crawler.get_standard_links')
    @patch('apra_crawler.extract_standard_details')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_logic_no_details_extracted(self, mock_builtin_open, mock_extract_details, mock_get_links, mock_create_dir):
        mock_get_links.return_value = [
            {'url': 'http://example.com/cps101', 'category': 'Governance', 'pillar': 'Core'}
        ]
        # extract_standard_details now returns (None, None) on failure
        mock_extract_details.return_value = (None, None)

        apra_crawler.main()

        mock_create_dir.assert_called_once()
        mock_get_links.assert_called_once_with(apra_crawler.BANKING_HANDBOOK_URL)
        mock_extract_details.assert_called_once_with('http://example.com/cps101', 'Governance', 'Core')
        mock_builtin_open.assert_not_called() # No data, so no CSV file


if __name__ == '__main__':
    unittest.main()


class TestConvertHtmlToMarkdown(unittest.TestCase):
    def test_basic_html_elements(self):
        html_input = "<p>Hello</p><h1>Heading</h1><ul><li>Item 1</li><li>Item 2</li></ul>"
        # Expected markdown can vary slightly based on markdownify's exact output and options.
        # We'll check for key structural elements and content.
        # Common markdownify output:
        # Hello\n\n# Heading\n\n* Item 1\n* Item 2
        expected_md_parts = [
            "Hello",
            "# Heading",
            "* Item 1",
            "* Item 2"
        ]
        markdown_output = apra_crawler.convert_html_to_markdown(html_input)

        # Normalize newlines and spacing for comparison if needed, or check parts.
        # For simplicity, check if parts are present and in reasonable structure.
        self.assertIn("Hello", markdown_output)
        # Check for Setext-style heading
        self.assertIn("Heading\n=======", markdown_output)
        self.assertIn("* Item 1", markdown_output) # or "- Item 1"
        self.assertIn("* Item 2", markdown_output) # or "- Item 2"

    def test_html_with_links(self):
        html_input = "<p>Here is a <a href='http://example.com'>link</a>.</p>"
        expected_markdown = "Here is a [link](http://example.com)."
        markdown_output = apra_crawler.convert_html_to_markdown(html_input)
        self.assertEqual(markdown_output.strip(), expected_markdown)

    def test_empty_html(self):
        html_input = ""
        expected_markdown = ""
        markdown_output = apra_crawler.convert_html_to_markdown(html_input)
        self.assertEqual(markdown_output.strip(), expected_markdown)

    def test_html_with_tables(self):
        html_input = "<table><thead><tr><th>Header 1</th><th>Header 2</th></tr></thead><tbody><tr><td>Data 1</td><td>Data 2</td></tr></tbody></table>"
        # Markdownify typically converts tables like this:
        # | Header 1 | Header 2 |
        # | -------- | -------- |
        # | Data 1   | Data 2   |
        markdown_output = apra_crawler.convert_html_to_markdown(html_input)

        # Check for key content and some structure
        self.assertIn("| Header 1 | Header 2 |", markdown_output)
        self.assertIn("| Data 1 | Data 2 |", markdown_output) # Adjusted spacing
        self.assertTrue(markdown_output.count('|') >= 6) # Basic check for table structure
        self.assertIn("---", markdown_output) # Separator line

    def test_ordered_list_conversion(self):
        html_input = "<ol><li>First item</li><li>Second item</li></ol>"
        # Expected:
        # 1. First item
        # 2. Second item
        markdown_output = apra_crawler.convert_html_to_markdown(html_input)
        # Normalize by splitting lines and stripping whitespace
        output_lines = [line.strip() for line in markdown_output.strip().split('\n')]
        expected_lines = [
            "1. First item",
            "2. Second item"
        ]
        self.assertEqual(output_lines, expected_lines)

    def test_explicit_paragraph_numbering(self):
        html_input = "<p>1. Explicit first.</p><p>2. Explicit second.</p>"
        # Expected:
        # 1. Explicit first.
        #
        # 2. Explicit second.
        # (markdownify usually adds blank lines between <p> tags)
        markdown_output = apra_crawler.convert_html_to_markdown(html_input)
        # Check for the core text, allowing for some flexibility in newlines
        self.assertIn("1. Explicit first.", markdown_output)
        self.assertIn("2. Explicit second.", markdown_output)
        # A more specific check if needed, after observing output:
        expected_parts = ["1. Explicit first.", "2. Explicit second."]
        normalized_output = "\n".join([line.strip() for line in markdown_output.strip().split('\n') if line.strip()])
        expected_output = "\n".join(expected_parts)
        # This might be too strict if markdownify adds more than one blank line.
        # Let's stick to assertIn for robustness or split and filter empty lines:
        output_lines = [line.strip() for line in markdown_output.strip().split('\n') if line.strip()]
        self.assertEqual(output_lines, expected_parts)


    def test_hr_tag_conversion(self):
        html_input = "<p>Some text</p><hr><p>Other text</p>"
        # Expected:
        # Some text
        #
        # ---
        #
        # Other text
        markdown_output = apra_crawler.convert_html_to_markdown(html_input)
        # Normalize whitespace and split into lines
        output_lines = [line.strip() for line in markdown_output.strip().split('\n')]
        # Filter out empty lines that markdownify might add around hr
        output_lines_filtered = [line for line in output_lines if line]

        expected_structure = [
            "Some text",
            "---",
            "Other text"
        ]
        self.assertEqual(output_lines_filtered, expected_structure)

    def test_bolded_paragraph_as_subheading(self):
        html_input = "<p><strong>This is a bold subheading</strong></p>"
        expected_markdown = "**This is a bold subheading**"
        markdown_output = apra_crawler.convert_html_to_markdown(html_input)
        self.assertEqual(markdown_output.strip(), expected_markdown)

    def test_standard_headings_regression(self):
        html_input = "<h2>A Standard Heading</h2><h3>A Sub-heading</h3>"
        # Expected (markdownify might use setext for H2 if it's the first/only heading):
        # A Standard Heading
        # ==================
        #
        # ### A Sub-heading
        # OR
        # ## A Standard Heading
        #
        # ### A Sub-heading
        markdown_output = apra_crawler.convert_html_to_markdown(html_input)

        # Check for presence of both heading texts
        self.assertIn("A Standard Heading", markdown_output)
        self.assertIn("A Sub-heading", markdown_output)

        # Check for markdown heading markers
        # This allows for either setext (H2) or atx (H2, H3)
        # Markdownify uses '---' for H2 setext style with default options
        is_setext_h2 = "A Standard Heading\n------------------" in markdown_output or \
                       "A Standard Heading\n---" in markdown_output # shorter line also possible
        is_atx_h2 = "## A Standard Heading" in markdown_output
        is_atx_h3 = "### A Sub-heading" in markdown_output

        self.assertTrue(is_setext_h2 or is_atx_h2, f"H2 marker not found in output:\n{markdown_output}")
        self.assertTrue(is_atx_h3, f"H3 marker not found in output:\n{markdown_output}")
