# 3D City Mapping

## Overview

This is a program that reads files containing 3D models of cities stored inside data models and renders them into a 3D Window. Current 
program can read only .xml and .city.gml files. For .city.json files, the program first converts the file to a GML file and then renders
the file into the window.

## Requirements

- Python 3.10
- VTK 9.1.0
- [Citygml tools 1.4.5](https://github.com/citygml4j/citygml-tools)

## Installation

1. Download or clone from the repository to your local device
```bash
git clone https://github.com/ParthCv/precisely-CityGML-mapping.git
```
2. Open the terminal inside the project
3. Run the following command to run the program
```bash
python driver.py data/twobuildings.city.gml --lod 2
```
## Commandline Arguments

- ```filepath``` - This is the path to the file containing the 3D model. The
filepath should be the path to a valid file and should be of .gml or .xml extension

- `lod` - This the level of detail that needs to be set while reading the file.
This is an optional argument and has a default value of 3. lod can range from 0 to 4.

- `force` - This is to force the overwriting of .gml a file if it's .json of the same name exist 
is it already exist while converting the json file. This is an optional argument and default is 
always false