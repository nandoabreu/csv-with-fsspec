"""My Python module

Description
"""
import requests
import xml.etree.ElementTree as ET
from itertools import islice


class Extractor:
    def __init__(self):
        ...

    @staticmethod
    def fetch_package_url(source_xml_url: str = None, link_index: int = 1):
        """Fetch the URL for the source ZIP file

        Args:
            source_xml_url (str): URL to the XML containing the required data
            link_index (int): Position in the XML data (structure: <result><doc><str name="download_link"/>...)

        Raises:
            requests.exception.ConnectionError: For errors while resolving the URL domain
            requests.exceptions.HTTPError: For errors while fetching the XML file
        """
        res = requests.get(source_xml_url)
        res.raise_for_status()

        root = ET.fromstring(res.content)
        url = next(islice(root.findall(".//str[@name='download_link']"), link_index, link_index + 1)).text

        return url

    def fetch_package_content(self):
        """Fetch the ZIP file content"""
        ...
