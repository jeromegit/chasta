import _csv
import argparse
import csv
import getpass
import os
import sys
from typing import List, Tuple, Union

import pandas as pd
import plotly.express as px

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
    return not is_row_all_digits(row)


def is_row_all_digits(row: List[str]) -> bool:
    try:
        # Try to convert each item in the row to a float
        for item in row:
            float(item)
        return True
    except ValueError:
        # If any conversion fails, return False
        return False


def determine_col_names(file_path: str, delimiter: str) -> Tuple[List[str], bool]:
    with open(file_path) as fd:
        try:
            header = csv.Sniffer().has_header(fd.read(1024))
        except _csv.Error as _:
            header = False
        fd.seek(0)
        reader = csv.reader(fd, delimiter=delimiter)
        first_row = next(reader)
        if header:
            return first_row, True
        else:
            col_count = len(first_row)
            col_names = [f"col_{col}" for col in range(0, col_count)]
            return col_names, False


def analyze_file(file_path: str, do_instance_count: bool = False, chart: Union[None, str] = None, delimiter: str = ',',
                 column: str = '0') -> Tuple[Union[None, pd.DataFrame], Union[pd.DataFrame, pd.Series, None]]:
    try:
        col_names, has_header = determine_col_names(file_path, delimiter)
        if has_header:
            df = pd.read_csv(file_path, sep=delimiter, names=col_names, skiprows=1)
        else:
            df = pd.read_csv(file_path, sep=delimiter, header=None)
    except FileNotFoundError:
        print(f"{file_path} No such file. Aborting.")
        return None, None

    column_names = []
    if Debug:
        print(df)
    column_types = set()
    df_columns = df.columns
    for col in column.split(','):
        column_name = determine_column_name(col, df_columns)
        column_names.append(column_name)
        column_types.add(df[column_name].dtypes)

    df_to_stats = df[column_names]
    if chart is None:
        df_to_chart = None
    else:
        if len(chart):
            chart_col = chart
            chart_column_name = determine_column_name(chart_col, df_columns)
            df_to_chart = df[[*column_names, chart_column_name]]
        else:
            df_to_chart = df_to_stats

    if do_instance_count:
        stats = df_to_stats.value_counts()
    else:
        stats = df_to_stats.describe(percentiles=[.25, .50, .75, .90, .95, .99, .999], include='all')
        if '50%' in stats.index:
            stats.loc['median'] = stats.loc['50%']

    return stats, df_to_chart


def print_stats(stats: Union[None, pd.DataFrame, pd.Series]) -> None:
    if stats is not None:
        if isinstance(stats, pd.DataFrame):
            print(f"Stats for column(s):{', '.join(stats.columns.astype(str))}:")
            print(stats)
        else:
            print(stats.to_string(dtype=False))


def chart(chart_df: pd.DataFrame, x_axis: Union[None, str]) -> None:
    fig = px.area(chart_df)
    # , y)=NEW_TO_ACK,
    #                  x='dt_in'
    # )
    fig.update_layout(hovermode='x unified')

    fig.show()
    with open('/tmp/chasta.html', 'w') as fd:
        fd.write(fig.to_html(include_plotlyjs='cdn'))

    fig.to_html()


def create_tmp_file_with_stdin() -> str:
    user_name = getpass.getuser()
    tmp_file_path = f'/tmp/chasta_{user_name}.tmp'
    with open(tmp_file_path, 'w') as fd:
        for line in sys.stdin:
            fd.write(line)

    return tmp_file_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a CSV file")
    parser.add_argument("-d", "--delimiter", type=str, default=",", help="column delimiter (default: ',')")
    parser.add_argument("-c", "--columns", type=str, default="0",
                        help="CSV list of column number(s) or name(s) to analyze (default: 0)")
    parser.add_argument("-C", "--chart", nargs='?', const='', default=None,
                        help="Chart column(s) optionally specifying the column number/name for the x-axis")
    parser.add_argument("-i", "--instance_count", action='store_true', help="Instance count")
    parser.add_argument("-n", "--num_only", action='store_true', help="Only consider numeric values")
    #    parser.add_argument("-u", "--use_header", action='store_true', help="Use provided headers")

    parser.add_argument("file", type=str, nargs='?', help="path to the CSV file or none for STDIN")

    return parser.parse_args()


def main():
    args = parse_args()
    if args.file:
        file_path = args.file
    else:
        file_path = create_tmp_file_with_stdin()
    stats_obj, chart_df = analyze_file(file_path, args.instance_count, args.chart, args.delimiter, args.columns)

    print_stats(stats_obj)

    if args.chart is not None:
        chart(chart_df, args.chart)

    if file_path != args.file:
        # clean up tmp STDIN file
        os.remove(file_path)

    if __name__ == "__main__":
        main()
