"""Extractor

This module holds the Extractor for the application's data
"""
from io import BytesIO
from zipfile import ZipFile

import requests
from lxml.etree import fromstring, parse
from pandas.core.frame import DataFrame


class Extractor:
    def __init__(self):
        ...

    @staticmethod
    def fetch_package_url(source_xml_url: str = None, link_index: int = 1) -> (None, str):
        """Fetch the URL for the source ZIP file

        Args:
            source_xml_url (str): URL to the XML containing the required data
            link_index (int): Position in the XML data (structure: <result><doc><str name="download_link"/>...)

        Returns:
            (str): Having the fetched URL

        Raises:
            requests.exception.ConnectionError: For errors while resolving the URL domain
            requests.exceptions.HTTPError: For errors while fetching the XML file
        """
        res = requests.get(source_xml_url)
        res.raise_for_status()

        root = fromstring(res.content)
        docs = root.findall(".//doc")
        if len(docs) < (link_index + 1):
            return

        i = 0
        for doc in docs:
            file_type = doc.find(".//str[@name='file_type']").text

            if file_type != 'DLTINS':
                continue

            if i == link_index:
                url = doc.find(".//str[@name='download_link']").text
                return url

            i += 1

    @staticmethod
    def parse_package_content(package_url: str) -> DataFrame:
        """Parse the ZIP file content

        Args:
            package_url (str): The URL to the ZIP package containing the XML data file

        Returns:
            DataFrame: A pandas dataframe
        """
        targeted_attributes = ['Id', 'FullNm', 'ClssfctnTp', 'CmmdtyDerivInd', 'NtnlCcy', 'Issr']
        df = DataFrame(columns=targeted_attributes)

        res = requests.get(package_url)
        res.raise_for_status()
        root = None

        with ZipFile(BytesIO(res.content)) as z:
            xml = z.namelist()[0]
            with z.open(xml) as f:
                root = parse(f).getroot()

        if root is not None:  # As for lxml deprecation (FutureWarning)
            temp_i = 0
            for fin_instrm_list in root.findall('.//{*}FinInstrm'):
                for fin_instrm in fin_instrm_list:
                    item = {
                        'Id': fin_instrm.find('.//{*}FinInstrmGnlAttrbts/{*}Id').text,
                        'FullNm': fin_instrm.find('.//{*}FinInstrmGnlAttrbts/{*}FullNm').text,
                        'ClssfctnTp': fin_instrm.find('.//{*}FinInstrmGnlAttrbts/{*}ClssfctnTp').text,
                        'CmmdtyDerivInd': fin_instrm.find('.//{*}FinInstrmGnlAttrbts/{*}CmmdtyDerivInd').text,
                        'NtnlCcy': fin_instrm.find('.//{*}FinInstrmGnlAttrbts/{*}NtnlCcy').text,
                        'Issr': fin_instrm.find('.//{*}Issr').text,
                    }

                    df = df._append(item, ignore_index=True)

                temp_i += 1
                if temp_i > 5:
                    break

        return df
