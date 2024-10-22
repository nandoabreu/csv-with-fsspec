import pytest
from unittest.mock import patch, MagicMock

from app.Extractor import Extractor


@pytest.fixture(scope='module')
def source_xml_path_var() -> str:
    return 'tests/samples/esma_file.xml'


@pytest.fixture(scope='module')
def source_xml_content_request_mock_obj(source_xml_path_var) -> str:
    mock = MagicMock()
    mock.status_code = 200

    with open(source_xml_path_var) as f:
        mock.content = f.read().encode()

    return mock

@pytest.fixture(scope='module')
def extractor_object():
    return Extractor()


@pytest.mark.parametrize(
    'link_index, expected_return', (
            (0, 'https://firds.esma.europa.eu/firds/DLTINS_20210117_01of01.zip'),
            (1, 'https://firds.esma.europa.eu/firds/DLTINS_20210119_01of02.zip'),
            (2, 'https://firds.esma.europa.eu/firds/DLTINS_20210119_02of02.zip'),
    ),
)
def method_fetch_package_url_test(extractor_object, source_xml_path_var, source_xml_content_request_mock_obj, link_index, expected_return):
    with patch('requests.get', return_value=source_xml_content_request_mock_obj):
        package_url = extractor_object.fetch_package_url(source_xml_url=source_xml_path_var, link_index=link_index)
        assert isinstance(package_url, str)
        assert package_url == expected_return
