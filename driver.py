import argparse
import filereaderfactory
import sys
import os

sys.path.append(os.path.dirname(__file__))


def setup_commandline_request():
    """
    Initializes commandline arguments, checks the inputs and calls the simulate function.
    :return:None
    """
    parser = argparse.ArgumentParser(description='Process a 3D Model.')
    parser.add_argument("filepath", help='a 3D model file')
    parser.add_argument("--lod", help='level of detail', nargs='?', choices=range(5), type=int)
    parser.add_argument("--force", help='force file conversion, default is false', action='store_true')

    args = parser.parse_args()
    filereaderfactory.FileReaderFactory.factory(args.filepath, args.lod, args.force)


def main():
    setup_commandline_request()


if __name__ == '__main__':
    main()
