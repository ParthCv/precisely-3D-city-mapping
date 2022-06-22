import argparse
import os.path
from pathlib import Path

from citygmlreader import CityGMLReader


def setup_commandline_request():
    """
    Initializes commandline arguments, checks the inputs and calls the simulate function.
    :return:None
    """
    parser = argparse.ArgumentParser(description='Process a 3D Model.')
    parser.add_argument("filepath", help='a 3D model file')
    parser.add_argument("--lod", help='level of detail', nargs='?', default=3, const=3, choices=range(5), type=int)

    args = parser.parse_args()
    filePath = Path(args.filepath)
    if filePath.is_file():
        split_tup = os.path.splitext(filePath)
        # extract the file extension
        file_extension = split_tup[1]
        validFileTypes = ['.gml', '.xml']
        if file_extension == '.gml' or file_extension == '.xml':
            try:
                CityGMLReader.simulate(filePath, args.lod)
            except Exception as e:
                print(f'Error: Something went wrong while reading the file.')
                print(e)
        else:
            print(f'Error: Invalid file extension!')
            print(f'Allowed file types {validFileTypes}')
    else:
        print(f'Error: file {filePath} does not exist!')


def main():
    setup_commandline_request()


if __name__ == '__main__':
    main()
