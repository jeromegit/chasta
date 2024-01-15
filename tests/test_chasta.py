from typing import List, Dict, Any, Union

import pytest

import chasta.chasta as cs

DEFAULT_DATA_FILE_PATH = '/tmp/chasta_test_data.txt'

DATA_3_ROWS_2_COLS = [[1, 10], [3, 30], [2, 20]]
DATA_3_ROWS_2_COLS_WITH_HEADER = [['single_digit', 'double_digit'], [1, 10], [3, 30], [2, 20]]


def data_to_file(data: str, file_path: str = DEFAULT_DATA_FILE_PATH):
    with open(file_path, "w") as fd:
        fd.write(data)

    return file_path


def convert_array_to_str(data: List[Any], delimiter: str) -> str:
    data_str = ''
    for row in data:
        if isinstance(row, list):
            data_str += delimiter.join(str(d) for d in row)
        else:
            data_str += str(row)
        data_str += "\n"

    return data_str


def analyze_numeric_data_expected_vs_actual(data: List[Any],
                                            expected_kvs: Union[Dict[str, float], List[Dict[str, float]]],
                                            delimiter: str = ',',
                                            cols: str = "0") -> None:
    if isinstance(data, list):
        data = convert_array_to_str(data, delimiter)
    actual = cs.analyze_file(data_to_file(data), delimiter, cols)

    if not isinstance(expected_kvs, list):
        expected_kvs = [expected_kvs]

    for expected_kv_index in range(len(expected_kvs)):
        expected_kv = expected_kvs[expected_kv_index]
        for k, expected in expected_kv.items():
            assert (k in actual.index), f"stat:{k} wasn't returned"
            actual_value = actual.loc[k] if len(actual.loc[k]) == 1 else actual.loc[k][expected_kv_index]
            assert float(actual_value) == float(expected), f"failed for key:{k} and index:{expected_kv_index}"


def test_determine_column_name():
    digit_col_names = ['col_0', 'col_1']
    assert cs.determine_column_name('0', digit_col_names), 'using column number'
    with pytest.raises(AssertionError) as ae:
        assert cs.determine_column_name('2', digit_col_names), 'using digit greater than max'
    assert "The specified column number can't be > 1" in str(ae.value)

    name_col_names = ['single_digit', 'double_digit']
    assert cs.determine_column_name('single_digit', name_col_names), 'using column name'
    with pytest.raises(AssertionError) as ae:
        assert cs.determine_column_name('bad_col_name', name_col_names), 'using digit greater than max'
    assert "The specified column name:bad_col_name is not in: single_digit, double_digit" in str(ae.value)


def test_is_row_a_header():
    assert cs.is_row_a_header('1,2,3'.split(',')) == False, 'all digits'
    assert cs.is_row_a_header('1.1,2.2,3.0'.split(',')) == False, 'all floats'
    assert cs.is_row_a_header('a,2,3'.split(',')) == True, 'one letter'
    assert cs.is_row_a_header('a,b,c'.split(',')) == True, 'all letters'


def test_single_column():
    analyze_numeric_data_expected_vs_actual([1, 2, 3, 4, 5, 6],
                                            {'count': 6, 'max': 6, 'min': 1, 'median': 3.5})


def test_single_column_with_different_separators():
    separators = [',', '|', ' ', '\t']
    for separator in separators:
        analyze_numeric_data_expected_vs_actual([1, 2, 3, 4, 5, 6],
                                                {'count': 6, 'max': 6, 'min': 1, 'median': 3.5}, separator)


def test_two_columns_use_first():
    analyze_numeric_data_expected_vs_actual(DATA_3_ROWS_2_COLS, {'count': 3, 'max': 3, 'min': 1, 'median': 2}, ',', '0')


def test_two_columns_use_second():
    analyze_numeric_data_expected_vs_actual(DATA_3_ROWS_2_COLS, {'count': 3, 'max': 30, 'min': 10, 'median': 20}, ',',
                                            '1')


def test_two_columns_use_both():
    analyze_numeric_data_expected_vs_actual(DATA_3_ROWS_2_COLS,
                                            [{'count': 3, 'max': 3, 'min': 1, 'median': 2},
                                             {'count': 3, 'max': 30, 'min': 10, 'median': 20}],
                                            ',',
                                            '0,1')


def test_analyze_file():
    actual = cs.analyze_file("/tmp/aa")
    assert actual is None, "Issue with missing file"


if __name__ == '__main__':
    pytest.main()