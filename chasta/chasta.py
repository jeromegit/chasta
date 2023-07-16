import argparse
import pandas as pd
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a CSV file")
    parser.add_argument("file", type=str, nargs='?', help="path to the CSV file")
    parser.add_argument("-d", "--delimiter", type=str, default=",", help="column delimiter (default: ',')")
    parser.add_argument("-c", "--column", type=str, default="0", help="column number or name to analyze (default: 0)")
    return parser.parse_args()


def determine_column_name(column: str, df: pd.DataFrame) -> str:
    if column.isdigit():
        column = int(column)
        assert column < len(df.columns), f"The specified column number can't be greater than > {len(df.columns) - 1}"
        column_name = df.columns[column]
    else:
        column_name = column

    return column_name


def analyze_file(file_path: str, delimiter: str, column: str) -> None:
    df = pd.read_csv(file_path, sep=delimiter)
    column_names = []
    for col in column.split(','):
        column_names.append(determine_column_name(col, df))
    stats = df[column_names].describe()
    print(f"Stats for column(s) '{column_names}':")
    print(stats)


def main():
    args = parse_args()
    if args.file:
        file_path = args.file
    else:
        file_path = sys.stdin
    analyze_file(file_path, args.delimiter, args.column)


if __name__ == "__main__":
    main()
