import os
import subprocess
from pathlib import Path

from citygmlreader import CityGMLReader


class CityJSONReader:

    @staticmethod
    def simulate(filePath, lod):
        """
        Validates and then converts a CityJSON file to a gml file and then renders the new gml file
        :param filePath: Path to a json file
        :param lod: level of detail
        :return: None
        """

        # Path to the city gml tool executable file to convert the file
        city_gml_tool_path = 'citygml-tools-1.4.5\\citygml-tools.bat'

        # Validate the CityJSON file before processing
        validate_file = subprocess.run(['cjio', filePath, 'validate'], capture_output=True, text=True)
        validate_file.check_returncode()

        try:
            # Run the command to convert the file
            subprocess.run(
                [city_gml_tool_path, 'from-cityjson', os.path.abspath(str(filePath))],
                capture_output=True,
                text=True,
                shell=True,
            )

            split_tup = os.path.splitext(filePath)
            # extract the file name
            file_name = split_tup[0]

            # The file path to new gml file
            new_file = Path(file_name + '.gml')

            # Check the file and render the gml file
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

