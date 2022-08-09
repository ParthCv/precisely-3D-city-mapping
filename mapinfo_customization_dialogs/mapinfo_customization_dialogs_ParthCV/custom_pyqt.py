import os
import os.path
import subprocess
from pathlib import Path

os.environ['QT_USE_NATIVE_WINDOWS'] = "1"
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import win32.win32gui
import win32.lib.win32con as win32con
import vtk
from vtk import vtkTexture, vtkImageReader2Factory
from vtkmodules.vtkIOCityGML import vtkCityGMLReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkPolyDataMapper
)


def __runcommand__(command):
    try:
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8', shell=True)
        p.wait()
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            if stdout:
                for line in stdout.strip().split("\n"):
                    print(line)
        elif p.returncode != 0:
            if stderr:
                for line in stderr.strip().split("\n"):
                    print(line)
    except Exception as e:
        print(e)


class CityGMLQTDialog(QDialog):
    def __init__(self, pro, city_gml_file, lod, force, *args, **kwargs):
        super(CityGMLQTDialog, self).__init__(*args, **kwargs)
        self.iren = None
        self.ren = vtkRenderer()
        self._pro = pro
        self._city_gml_file = city_gml_file
        self._lod = int(lod) if str(lod).isdigit() else None
        self._force = force

        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("3D Surfaces")
        self.resize(500, 500)

        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vl.addWidget(self.vtkWidget)

        self.setLayout(self.vl)

    def factory(self):
        """
        Factory method to call respective file readers based on the file extension
        :return: None
        """
        filePath = Path(self._city_gml_file)
        if filePath.is_file():
            split_tup = os.path.splitext(filePath)
            # extract the file extension
            file_extension = split_tup[1]
            validFileTypes = ['.gml', '.xml', '.json']
            if file_extension == '.gml' or file_extension == '.xml':
                try:
                    if self._lod is None:
                        self.readCityGML()
                    else:
                        self.readCityGMLWithLod()
                except Exception as e:
                    print(f'Error: Something went wrong while reading the file.')
                    print(e)
            elif file_extension == '.json':
                try:
                    self.convertCityJSONtoCityGML()
                except Exception as e:
                    print(f'Error: Something went wrong while reading the file.')
                    print(e)
            else:
                print(f'Error: Invalid file extension!')
                print(f'Allowed file types {validFileTypes}')
        else:
            print(f'Error: file {filePath} does not exist!')

    def readCityGMLWithLod(self):
        """
        Reads the .gml file and processes it in a 3D Model window
        :return: None
        """

        # Turn off all the warnings.
        vtk.vtkObject.GlobalWarningDisplayOff()

        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        # The renderer renders into the render window. And set the background.
        self.ren.SetBackground(0.5, 0.7, 0.7)

        try:
            print(f"Reading {self._city_gml_file} file")

            # Initialize the CityGML reader and set the file path
            reader = vtkCityGMLReader()
            reader.SetFileName(self._city_gml_file)

            # Specify the level of detail to read (0-4) [default - 3]
            reader.SetLOD(self._lod)

            # Brings the reader up-to-date
            reader.Update()

            # Call function to render the objets in the renderer
            self.render_data(reader)

            # Automatically sets up the camera based on the bound
            self.ren.ResetCamera()

            # We get the current camera with GetActiveCamera
            # Azimuth - horizontal rotation of the camera
            # Roll - Spin the camera around its axis
            # Zoom - zooms in (>1) or out (<1) based on the factor
            self.ren.GetActiveCamera().Azimuth(90)
            self.ren.GetActiveCamera().Roll(-90)
            self.ren.GetActiveCamera().Zoom(1.5)

            # Start the event loop
            self.iren.Start()

        except Exception as e:
            print(f'Error: Something went wrong while processing the file.')
            print(e)

    def readCityGML(self):
        """
        Reads the .gml file and processes it in a 3D Model window
        """

        # Turn off all the warnings.
        vtk.vtkObject.GlobalWarningDisplayOff()

        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        # The renderer renders into the render window. And set the background.
        self.ren.SetBackground(0.5, 0.7, 0.7)

        # The order to try out different level of details
        lodOrder = [3, 1, 2, 4]

        try:
            print(f"Reading {self._city_gml_file} file")

            # Initialize the CityGML reader and set the file path
            reader = vtkCityGMLReader()
            reader.SetFileName(self._city_gml_file)

            # Loop through all level of details until correct one is found
            for lod in lodOrder:
                print(f"Trying with lod {lod}")

                # Specify the level of detail to read (0-4) [default - 3]
                reader.SetLOD(lod)

                # Brings the reader up-to-date
                reader.Update()

                # Call function to render the objets in the renderer and
                # get the count of times it ran for the specific lod
                count = self.render_data(reader)

                # Check if this lod had data if so break out of the loop
                if count > 0:
                    print(f"Data found on lod {lod}")
                    break
                print(f"No Data found on lod {lod}")

            # Automatically sets up the camera based on the bound
            self.ren.ResetCamera()

            # We get the current camera with GetActiveCamera
            # Azimuth - horizontal rotation of the camera
            # Roll - Spin the camera around its axis
            # Zoom - zooms in (>1) or out (<1) based on the factor
            self.ren.GetActiveCamera().Azimuth(90)
            self.ren.GetActiveCamera().Roll(-90)
            self.ren.GetActiveCamera().Zoom(1.5)

            # Start the event loop
            self.iren.Start()

        except Exception as e:
            print(f'Error: Something went wrong while processing the file.')
            print(e)

    def convertCityJSONtoCityGML(self):
        """
        Validates and then converts a CityJSON file to a gml file and then renders the new gml file
        :return: None
        """

        print(f"Reading {self._city_gml_file} file.")

        # Path to the city gml tool executable file to convert the file
        city_gml_tool_path = os.path.dirname(__file__) + '.\\citygml-tools-1.4.5\\citygml-tools.bat'

        split_tup = os.path.splitext(self._city_gml_file)
        # extract the file name
        file_name = split_tup[0]

        # The file path to new gml file
        self._city_gml_file = Path(file_name + '.gml')
        file_name = Path(file_name + '.json')
        print()
        # check for existing file
        if self._city_gml_file.is_file() and not self._force:
            print(f"File {self._city_gml_file} already exits, to overwrite this use '--force'")
            if self._lod is None:
                self.readCityGML()
            else:
                self.readCityGMLWithLod()
        else:
            try:
                print(f"Converting {file_name} to a gml file.")

                # Run the command to convert the file
                __runcommand__([city_gml_tool_path, 'from-cityjson', os.path.abspath(str(file_name))])

                # Check the file and render the gml file
                if self._city_gml_file.is_file():
                    print(f"File conversion successful. Rendering the GML file now")
                    if self._lod is None:
                        self.readCityGML()
                    else:
                        self.readCityGMLWithLod()
                else:
                    raise Exception('Error: File Not Converted')

            except Exception as e:
                print(f'Error: Something went wrong while converting the file.')
                print(e)

    def render_data(self, reader):
        """
        Render the blocks of data to the renderer.

        :param reader: the cityGML reader object
        :return: the number of time the while loop executed
        """

        # multi block dataset - organizes a dataset into blocks
        mb = reader.GetOutput()

        # Create image reader factory object
        createReader = vtkImageReader2Factory()

        # Set an iterator to read over all the blocks in the dataset.
        # And an object to always store current data object
        it = mb.NewIterator()
        obj = it.GetCurrentDataObject()

        # variable to keep the count of times while loop ran
        count = 0

        while obj:
            # This is a PolyData object which represents a geometric structure
            # consisting of vertices, lines, polygons, and/or triangle strips
            poly = it.GetCurrentDataObject()

            if poly:
                count += 1
                # This mapper helps map the polygonal data to graphics primitives,
                # that are the basic objects for the creation of complex images.
                mapper = vtkPolyDataMapper()
                mapper.SetInputDataObject(poly)

                # Used to represent an object in a rendered scene. Set the mapper
                # to tha actor and add it to the renderer
                actor = vtkActor()
                actor.SetMapper(mapper)
                self.ren.AddActor(actor)

                # Retrieve the general field data and get the array with the name texture-uri,
                # which contains the path to the texture file.
                textureField = poly.GetFieldData().GetAbstractArray('texture_uri')
                if textureField:
                    textureURI = textureField.GetValue(0)

                    # complete path to the texture file and read it as an image
                    strFilePath = os.path.dirname(os.path.abspath(str(self._city_gml_file)))
                    path = strFilePath + '/' + textureURI

                    if os.path.isfile(path):
                        imgReader = createReader.CreateImageReader2(path)
                        imgReader.SetFileName(path)

                        # We create a texture object which handles the loading and binding if texture maps
                        # We set the connection for the given input port index, this also removes  all other
                        # connections from the port. To add the port we use GetOutputPort on the image reader
                        texture = vtkTexture()
                        texture.SetInputConnection(imgReader.GetOutputPort())

                        # turns the linear interpolation on. which means to estimate an unknown value from given
                        # data assuming the curve is a straight line.
                        texture.InterpolateOn()

                        # set the texture of the current actor.
                        actor.SetTexture(texture)

            # iterate to the next block
            it.GoToNextItem()
            obj = it.GetCurrentDataObject()

        return count

    def showDialog(self, proHwnd):
        # Call the file factory function
        self.factory()
        self.show()
        # Get QT Dialog handle
        dhwnd = int(self.winId())

        # reparent the qt dialog into MapInfo Pro.
        win32.win32gui.SetWindowLong(dhwnd, win32con.GWL_HWNDPARENT, proHwnd)
        win32.win32gui.EnableWindow(proHwnd, 0)
        self.exec_()

        win32.win32gui.EnableWindow(proHwnd, 1)
        win32.win32gui.SetForegroundWindow(proHwnd)
