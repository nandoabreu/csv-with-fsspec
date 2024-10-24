import pytest
from tempfile import gettempdir, mkdtemp

from pandas.core.frame import DataFrame

from app.Storage import Storage


@pytest.mark.skip('This module was refactored - Unit tests pending')
@pytest.mark.parametrize(
    'attrs, expected, error', [
        ({}, [False], ['directory not set']),

        ({'local_dir': None}, [False], ['directory not set']),
        ({'local_dir': gettempdir()}, [True], [None]),
        ({'local_dir': f'{mkdtemp()}/pytest'}, [True], [None]),
        ({'local_dir': '/root'}, [False], ['could not write in directory']),

        ({'azure_conn_string_file': None}, [None], [None]),
        ({'azure_container': None}, [False], [None]),

        ({'local_dir': None, 'azure_conn_string_file': None}, [False, False], ['directory not set', 'connection not set']),
],
)
def storage_object_test(attrs, expected, error):
    obj = Storage(**attrs)
    tested = []
    print(f'{attrs}: {obj.status=}')

    if not attrs:
        assert obj.status['local']['valid'] is expected[0]
        assert obj.status['local']['error'] == error[0]
        tested.append('local')

    for i, ref in enumerate(attrs):
        ref = ref.split('_')[0]
        if ref in tested:
            continue  # Prevent testing twice if more than one ref key if send (i.e.: aws_X, aws_Y)

        assert obj.status.get(ref, {}).get('valid') is expected[i]
        assert obj.status.get(ref, {}).get('error') == error[i]
        tested.append(ref)


@pytest.mark.skip('This module was refactored - Unit tests pending')
def store_data_in_local_csv_test(work_dir_var):
    df = DataFrame([1, 2, 3], columns=['FullNm'])
    obj = Storage(local_dir=work_dir_var)
    obj.store_csv(df, 'pytest.csv')
