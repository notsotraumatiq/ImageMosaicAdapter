import argparse
import json
import itertools

def read_file(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f]

def create_json(filenames, columns, rows):
    file_entries = read_file(filenames)
    iterator = itertools.cycle(file_entries)
    json_data = []
    entries_count = len(file_entries)
    processed_entries = 0

    while processed_entries < entries_count:
        chunk = [[next(iterator) for _ in range(columns)] for _ in range(rows)]
        json_data.append(chunk)
        processed_entries += columns * rows

    return json.dumps(json_data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filenames', type=str, required=True, help='Path to the text file.')
    parser.add_argument('--columns', type=int, required=True, help='Number of columns.')
    parser.add_argument('--rows', type=int, required=True, help='Number of rows.')
    args = parser.parse_args()

    print(create_json(args.filenames, args.columns, args.rows))

if __name__ == "__main__":
    main()
