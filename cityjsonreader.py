import os
import subprocess
from pathlib import Path

from citygmlreader import CityGMLReader


class CityJSONReader:

    @staticmethod
    def simulate(filePath, lod):
        city_gml_tool_path = 'citygml-tools-1.4.5\\citygml-tools.bat'

        validate_file = subprocess.run(['cjio', filePath, 'validate'], capture_output=True, text=True)
        validate_file.check_returncode()

        try:
            subprocess.run(
                [city_gml_tool_path, 'from-cityjson', os.path.abspath(str(filePath))],
                capture_output=True,
                text=True,
                shell=True,
            )

            split_tup = os.path.splitext(filePath)
            # extract the file name
            file_name = split_tup[0]
            new_file = Path(file_name + '.gml')

            if new_file.is_file():
                if lod is None:
                    CityGMLReader.simulateWithoutLOD(new_file)
                else:
                    CityGMLReader.simulateWithLOD(new_file, lod)
            else:
                raise Exception('Error: File Not Converted')

        except Exception as e:
            print(f'Error: Something went wrong while converting the file.')
            print(e)

