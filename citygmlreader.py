from pathlib import Path

from vtk import vtkCityGMLReader
from vtk import vtkImageReader2Factory
from vtk import vtkTexture
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkPolyDataMapper
)


class CityGMLReader:

    @staticmethod
    def simulate(filePath, lod: int):
        """
        Reads the .gml file and processes it in a 3D Model window
        :param lod: Level of detail
        :param filePath: Path to the .gml file
        :return: None
        """

        # The renderer renders into the render window. And set the background.
        ren = vtkRenderer()
        ren.SetBackground(0.5, 0.7, 0.7)

        # The render window interactor captures mouse events and will
        # perform appropriate camera or actor manipulation depending on the
        # nature of the events.
        renWin = vtkRenderWindow()
        renWin.AddRenderer(ren)

        iren = vtkRenderWindowInteractor()
        iren.SetRenderWindow(renWin)

        try:
            # Initialize the CityGML reader and set the file path
            reader = vtkCityGMLReader()
            reader.SetFileName(filePath)

            # Specify the level of detail to read (0-4) [default - 3]
            reader.SetLOD(lod)

            # Brings the reader up-to-date
            reader.Update()

            # multi block dataset - organizes a dataset into blocks
            mb = reader.GetOutput()

            # Create image reader factory object
            createReader = vtkImageReader2Factory()

            # Set an iterator to read over all the blocks in the dataset.
            # And an object to always store current data object
            it = mb.NewIterator()
            obj = it.GetCurrentDataObject()

            while obj:
                # This is a PolyData object which represents a geometric structure
                # consisting of vertices, lines, polygons, and/or triangle strips
                poly = it.GetCurrentDataObject()

                if poly:

                    # This mapper helps map the polygonal data to graphics primitives,
                    # that are the basic objects for the creation of complex images.
                    mapper = vtkPolyDataMapper()
                    mapper.SetInputDataObject(poly)

                    # Used to represent an object in a rendered scene. Set the mapper
                    # to tha actor and add it to the renderer
                    actor = vtkActor()
                    actor.SetMapper(mapper)
                    ren.AddActor(actor)

                    # Retrieve the general field data and get the array with the name texture-uri,
                    # which contains the path to the texture file.
                    textureField = poly.GetFieldData().GetAbstractArray('texture_uri')
                    if textureField:
                        textureURI = textureField.GetValue(0)

                        # complete path to the texture file and read it as an image
                        strFilePath = str(filePath)
                        path = strFilePath + '/' + textureURI

                        if Path(path):
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

            # Automatically sets up the camera based on the bound
            ren.ResetCamera()

            # We get the current camera with GetActiveCamera
            # Azimuth - horizontal rotation of the camera
            # Roll - Spin the camera around its axis
            # Zoom - zooms in (>1) or out (<1) based on the factor
            ren.GetActiveCamera().Azimuth(90)
            ren.GetActiveCamera().Roll(90)
            ren.GetActiveCamera().Zoom(1.5)

            # Set the size of the rendering window in pixels
            renWin.SetSize(400, 400)

            # Ask each viewport in the render window to render its image
            renWin.Render()

            # Prepare for handling events and set the Enabled flag to true.
            iren.Initialize()
            renWin.Render()

            # Start the event loop
            iren.Start()

        except Exception as e:
            print(f'Error: Something went wrong while processing the file.')
            print(e)
