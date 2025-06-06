import unittest
from unittest.mock import patch, MagicMock, mock_open
import io
import csv

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

        result = apra_crawler.extract_standard_details(url, category, pillar)
        self.assertEqual(result, expected_details)

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

        result = apra_crawler.extract_standard_details(url, category, pillar)
        self.assertEqual(result, expected_details)

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

        result = apra_crawler.extract_standard_details(url, category, pillar)
        self.assertEqual(result, expected_details)

    @patch('apra_crawler.requests.get')
    def test_extract_details_network_error(self, mock_requests_get):
        mock_requests_get.side_effect = apra_crawler.requests.exceptions.RequestException("Test network error")

        result = apra_crawler.extract_standard_details("https://example.com/error-page", "ErrorCategory", "ErrorPillar")
        self.assertIsNone(result)

class TestMainScript(unittest.TestCase):
    # Patch target is 'apra_crawler.get_standard_links' because main() in apra_crawler.py will call it from its own module.
    @patch('apra_crawler.get_standard_links')
    @patch('apra_crawler.extract_standard_details')
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictWriter')
    # Note: The order of mock arguments to the test function is from bottom-up for decorators.
    def test_main_logic_with_data_and_csv_writing(self, mock_csv_dict_writer, mock_builtin_open, mock_extract_details, mock_get_links):
        # 1. Setup Mocks
        mock_get_links.return_value = [
            {'url': 'http://example.com/cps101', 'category': 'Governance', 'pillar': 'Core'},
            {'url': 'http://example.com/sps202', 'category': 'Risk', 'pillar': 'Supporting'}
        ]

        expected_data_from_extract = [
            {'title': 'CPS 101', 'url': 'http://example.com/cps101', 'status': 'Current', 'date': 'Jan 2023', 'category': 'Governance', 'pillar': 'Core'},
            {'title': 'SPS 202', 'url': 'http://example.com/sps202', 'status': 'Draft', 'date': 'Feb 2024', 'category': 'Risk', 'pillar': 'Supporting'}
        ]
        mock_extract_details.side_effect = expected_data_from_extract

        mock_writer_instance = MagicMock()
        mock_csv_dict_writer.return_value = mock_writer_instance

        # 2. Call the main function from apra_crawler
        # The BANKING_HANDBOOK_URL is hardcoded in apra_crawler.main, so we don't need to pass it.
        # The output_csv_file is also hardcoded.
        returned_data = apra_crawler.main()

        # 3. Assertions
        # BANKING_HANDBOOK_URL is used by apra_crawler.main() internally
        mock_get_links.assert_called_once_with(apra_crawler.BANKING_HANDBOOK_URL)
        self.assertEqual(mock_extract_details.call_count, 2)
        mock_extract_details.assert_any_call('http://example.com/cps101', 'Governance', 'Core')
        mock_extract_details.assert_any_call('http://example.com/sps202', 'Risk', 'Supporting')

        # Check that the data returned by main() is what we expect
        self.assertEqual(returned_data, expected_data_from_extract)

        # Check CSV writing
        # output_csv_file is hardcoded in apra_crawler.main() as "apra_banking_standards.csv"
        mock_builtin_open.assert_called_once_with("apra_banking_standards.csv", 'w', newline='', encoding='utf-8')
        mock_csv_dict_writer.assert_called_once_with(mock_builtin_open(), fieldnames=["title", "url", "status", "date", "category", "pillar"])
        mock_writer_instance.writeheader.assert_called_once()
        mock_writer_instance.writerows.assert_called_once_with(expected_data_from_extract)

    @patch('apra_crawler.get_standard_links')
    @patch('apra_crawler.extract_standard_details')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_logic_no_links_found(self, mock_builtin_open, mock_extract_details, mock_get_links):
        mock_get_links.return_value = [] # No links found

        apra_crawler.main()

        mock_get_links.assert_called_once_with(apra_crawler.BANKING_HANDBOOK_URL)
        mock_extract_details.assert_not_called()
        mock_builtin_open.assert_not_called() # CSV file should not be opened

    @patch('apra_crawler.get_standard_links')
    @patch('apra_crawler.extract_standard_details')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_logic_no_details_extracted(self, mock_builtin_open, mock_extract_details, mock_get_links):
        mock_get_links.return_value = [
            {'url': 'http://example.com/cps101', 'category': 'Governance', 'pillar': 'Core'}
        ]
        mock_extract_details.return_value = None # Simulate extraction failure

        apra_crawler.main()

        mock_get_links.assert_called_once_with(apra_crawler.BANKING_HANDBOOK_URL)
        mock_extract_details.assert_called_once_with('http://example.com/cps101', 'Governance', 'Core')
        mock_builtin_open.assert_not_called() # No data, so no CSV file


if __name__ == '__main__':
    unittest.main()
