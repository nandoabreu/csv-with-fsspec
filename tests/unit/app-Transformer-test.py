import pytest

from pandas.core.frame import DataFrame

from app.Transformer import Transformer


data_test = [
    # Syntax: (str, int (number of "a"s in str))
    ('Lorem ipsum dolor', 0),
    ('Sed ut perspiciatis unde omnis iste natus error', 2),
    ('Li Europan lingues es membres del sam familie', 3),
    ('There is no lower A here', 0),
    ('There is one lowercase A here', 1),
]
df = DataFrame([i[0] for i in data_test], columns=['FullNm'])


@pytest.fixture(scope='module')
def transformer_object():
    return Transformer()


def method_create_derived_columns_test(transformer_object):
    transformer_object.create_derived_columns(df)
    assert 'a_count' in df.columns
    assert 'contains_a' in df.columns


@pytest.mark.parametrize('i, data_test', enumerate(data_test))
def method_validate_derived_columns_test(i, data_test):
    string, expected_count = data_test
    assert df.iloc[i, 0] == string
    assert df.iloc[i, -2] == expected_count
    assert df.iloc[i, -1] == 'YES' if expected_count else 'NO'
