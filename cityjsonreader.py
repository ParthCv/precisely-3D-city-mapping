import os
import subprocess
from pathlib import Path
from citygmlreader import CityGMLReader


class CityJSONReader:

    @staticmethod
    def simulate(filePath, lod, force):
        """
        Validates and then converts a CityJSON file to a gml file and then renders the new gml file
        :param filePath: Path to a json file
        :param lod: level of detail
        :return: None
        """

        print(f"Reading {filePath} file.")

        # Path to the city gml tool executable file to convert the file
        city_gml_tool_path = 'citygml-tools-1.4.5\\citygml-tools.bat'

        split_tup = os.path.splitext(filePath)
        # extract the file name
        file_name = split_tup[0]

        # The file path to new gml file
        new_file = Path(file_name + '.gml')

        # check for existing file
        if new_file.is_file() and not force:
            print(f"File {new_file} already exits, to overwrite this use '--force'")
            if lod is None:
                CityGMLReader.simulateWithoutLOD(new_file)
            else:
                CityGMLReader.simulateWithLOD(new_file, lod)
        else:
            try:
                print(f"Converting {filePath} to a gml file.")

                # Run the command to convert the file
                subprocess.run(
                    [city_gml_tool_path, 'from-cityjson', os.path.abspath(str(filePath))],
                    capture_output=True,
                    text=True,
                    shell=True,
                )

                # Check the file and render the gml file
                if new_file.is_file():
                    print(f"File conversion successful. Rendering the GML file now")
                    if lod is None:
                        CityGMLReader.simulateWithoutLOD(new_file)
                    else:
                        CityGMLReader.simulateWithLOD(new_file, lod)
                else:
                    raise Exception('Error: File Not Converted')

            except Exception as e:
                print(f'Error: Something went wrong while converting the file.')
                print(e)
