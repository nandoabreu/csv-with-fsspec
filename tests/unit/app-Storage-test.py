import pytest
from tempfile import gettempdir, mkdtemp

from pandas.core.frame import DataFrame

from app.Storage import Storage


@pytest.mark.parametrize(
    'attrs, expected, error', [
        ({}, [False], ['directory not set']),
        ({'local_dir': None}, [False], ['directory not set']),
        ({'local_dir': gettempdir()}, [True], [None]),
        ({'local_dir': f'{mkdtemp()}/pytest'}, [True], [None]),
        ({'local_dir': '/root'}, [False], ['could not write in directory']),
    ],
)
def storage_object_test(attrs, expected, error):
    obj = Storage(**attrs)

    if not attrs:
        assert obj.status['local']['valid'] is expected[0]
        assert obj.status['local']['error'] == error[0]

    prev = None
    for i, ref in enumerate(attrs):
        ref = ref.split('_')[0]
        if prev and ref == prev:
            continue  # Prevent testing twice if more than one ref key if present

        assert obj.status[ref]['valid'] is expected[i]
        assert obj.status[ref]['error'] == error[i]
        prev = ref


def store_data_in_local_csv_test(work_dir_var):
    df = DataFrame([1, 2, 3], columns=['FullNm'])
    obj = Storage(local_dir=work_dir_var)
    obj.store_csv(df, 'pytest.csv')
