"""My Python module

Description
"""
import requests
import xml.etree.ElementTree as ET


class Extractor:
    def __init__(self):
        ...

    def fetch_package_url(self, source_xml_url: str = None, link_index: int = 1):
        """Fetch the URL for the source ZIP file"""
        res = requests.get(source_xml_url)
        res.raise_for_status()

        root = ET.fromstring(res.content)
        download_links = [element.text for element in root.findall('.//str[@name="download_link"]')]
        print(download_links)

    def fetch_package_content(self):
        """Fetch the ZIP file content"""
        ...
