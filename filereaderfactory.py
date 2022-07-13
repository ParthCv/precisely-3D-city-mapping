import os.path
from pathlib import Path
from citygmlreader import CityGMLReader
from cityjsonreader import CityJSONReader


class FileReaderFactory:

    @staticmethod
    def factory(filepath, lod):
        filePath = Path(filepath)
        if filePath.is_file():
            split_tup = os.path.splitext(filePath)
            # extract the file extension
            file_extension = split_tup[1]
            validFileTypes = ['.gml', '.xml', '.json']
            if file_extension == '.gml' or file_extension == '.xml':
                try:
                    if lod is None:
                        CityGMLReader.simulateWithoutLOD(filePath)
                    else:
                        CityGMLReader.simulateWithLOD(filePath, lod)
                except Exception as e:
                    print(f'Error: Something went wrong while reading the file.')
                    print(e)
            elif file_extension == '.json':
                CityJSONReader.simulate(filePath, lod)
            else:
                print(f'Error: Invalid file extension!')
                print(f'Allowed file types {validFileTypes}')
        else:
            print(f'Error: file {filePath} does not exist!')
