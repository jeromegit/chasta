import argparse
import csv
import sys
from typing import List, Tuple, Set, Any, Union

import numpy as np
import pandas as pd

Debug = False


def determine_column_name(column: str, df_columns: List[str]) -> str:
    if column.isdigit():
        column = int(column)
        assert column < len(df_columns), f"The specified column number can't be > {len(df_columns) - 1}"
        column_name = df_columns[column]
    else:
        assert column in df_columns, f"The specified column name:{column} is not in: {', '.join(df_columns)}"
        column_name = column

    return column_name


def is_row_a_header(row: List[str]) -> bool:
    return any(not value.replace('.', '', 1).isdigit() for value in row)


def is_row_all_digits(row: List[str]) -> bool:
    return all(col.isdigit() for col in row)


def determine_col_names(file_path: str, delimiter: str) -> Tuple[List[str], bool]:
    with open(file_path) as fd:
        reader = csv.reader(fd, delimiter=delimiter)
        first_line = next(reader)
        second_line = next(reader)
        if is_row_a_header(first_line) and is_row_all_digits(second_line):
            return first_line, True
        else:
            col_count = len(first_line)
            col_names = [f"col_{col}" for col in range(0, col_count)]
            return col_names, False


def determine_types(dtypes: Set[Any]) -> Tuple[bool, bool, bool]:
    num_types = 0
    non_num_types = 0
    for dtype in dtypes:
        if np.issubdtype(dtype, np.number):
            num_types += 1
        else:
            non_num_types += 1

    is_num_only = num_types > 0 and non_num_types == 0
    is_non_num_only = non_num_types > 0 and num_types == 0
    is_mixed = num_types > 0 and non_num_types > 0

    return is_num_only, is_non_num_only, is_mixed


def analyze_file(file_path: str, do_instance_count: bool = False, delimiter: str = ',', column: str = '0') -> Union[
    pd.DataFrame, pd.Series, None]:
    try:
        col_names, has_header = determine_col_names(file_path, delimiter)
        if has_header:
            df = pd.read_csv(file_path, sep=delimiter, names=col_names, skiprows=1)
        else:
            df = pd.read_csv(file_path, sep=delimiter, header=None)
    except FileNotFoundError:
        print(f"{file_path} No such file. Aborting.")
        return None

    column_names = []
    if Debug:
        print(df)
    column_types = set()
    df_columns = df.columns
    for col in column.split(','):
        column_name = determine_column_name(col, df_columns)
        column_names.append(column_name)
        # if num_only:
        #     df = df[pd.to_numeric(df[column_name], errors='coerce').notnull()]
        column_types.add(df[column_name].dtypes)

    df = df[column_names]

    is_num_only, is_non_num_only, is_mixed = determine_types(column_types)
    if is_mixed:
        include = 'all'
    #    print(df)

    if do_instance_count:
        stats = df.value_counts()
    else:
        stats = df.describe(percentiles=[.25, .50, .75, .90, .95, .99, .999], include='all')
        if not is_non_num_only:
            stats.loc['median'] = df.describe().loc[['50%']].values[0]
    if Debug:
        print('-' * 80)
        print(df.value_counts())
        print('-' * 80)
        print(df.dtypes)
        print('-' * 80)

    return stats


def print_stats(stats: Union[None, pd.DataFrame, pd.Series]) -> None:
    if stats is not None:
        if isinstance(stats, pd.DataFrame):
            print(f"Stats for column(s):{', '.join(stats.columns.astype(str))}:")
            print(stats)
        else:
            print(stats.to_string(dtype=False))



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a CSV file")
    parser.add_argument("-d", "--delimiter", type=str, default=",", help="column delimiter (default: ',')")
    parser.add_argument("-c", "--columns", type=str, default="0",
                        help="CSV column number(s) or name(s) to analyze (default: 0)")
    parser.add_argument("-i", "--instance_count", action='store_true', help="Instance count")
    parser.add_argument("-n", "--num_only", action='store_true', help="Only consider numeric values")
    #    parser.add_argument("-u", "--use_header", action='store_true', help="Use provided headers")

    parser.add_argument("file", type=str, nargs='?', help="path to the CSV file")

    return parser.parse_args()


def main():
    args = parse_args()
    if args.file:
        file_path = args.file
    else:
        file_path = sys.stdin
    stats_df = analyze_file(file_path, args.instance_count, args.delimiter, args.columns)
    print_stats(stats_df)


if __name__ == "__main__":
    main()
