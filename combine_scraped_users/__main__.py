import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List
from tqdm import tqdm


parser = argparse.ArgumentParser(prog='Linkedin Scraper', description='Scrapes linkedin profiles from a search term')


@dataclass
class Args:
    """Class that contains the data from parsing args"""
    directory: str
    output_name: str
    input_files: List[str]


def main(p_args: Args) -> None:
    directory, output_name, input_files = p_args.directory, p_args.output_name, p_args.input_files
    directory_path = Path(directory)
    if not directory_path.is_dir():
        raise Exception(f"{directory=} is not a valid directory")
    valid_input_paths = [(directory_path / input_filename).is_file() for input_filename in input_files]
    if not all(valid_input_paths):
        raise Exception(f'Not all valid input paths')
    combined_users = []

    for input_filename in tqdm(input_files):
        input_filepath = directory_path / input_filename
        with open(input_filepath, 'r') as input_file:
            input_json = json.load(input_file)
            for user in input_json:
                combined_users.append(user)

    if not output_name.endswith('.json'):
        output_filepath = directory_path / f'{output_name}.json'
    else:
        output_filepath = directory_path / output_name

    with open(output_filepath, 'w') as output_file:
        json.dump(combined_users, output_file, indent=4)


if __name__ == '__main__':
    parser.add_argument('input_files', nargs='+')
    parser.add_argument('-dir', '--directory', type=str, help='The directory to look at the json', required=True)
    parser.add_argument('-out', '--output_name', type=str, default='combined.json',
                        help='The filename for the combined output json file')

    args = parser.parse_args()
    parsed_args = Args(directory=args.directory, output_name=args.output_name, input_files=args.input_files)

    main(parsed_args)
