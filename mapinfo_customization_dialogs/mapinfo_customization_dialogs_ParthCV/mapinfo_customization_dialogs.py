# MapInfo Pro Sample Addin to show on how to customize MapInfo Pro Ribbon Interface and add dialogs to it.

# Script Needs PyQt5 module to be installed in MapInfo Pro Python Environment to run.
# To Install PyQt5 module in Launch Python Console in MapInfo Pro from Home->Windows->Tool Window Gallery
# Type install_module("PyQT5") and press Control + Enter.

import sys
import os
from System import String, Object, Int32
from System.Collections.Generic import List
from os.path import join, dirname

os.environ['QT_USE_NATIVE_WINDOWS'] = "1"

# uncomment these lines to debug the python script using VSCODE
# need to install ptvsd package into your environment using "pip install ptvsd"
# import ptvsd

sys.path.append(join(dirname(__file__), "..\\"))

import clr
# TODO: import types as needed.
from MapInfo.Types import MessageOutput
from mi_common_util import CommonUtil
from mi_addin_util import AddinUtil
from PyQt5.QtWidgets import QApplication
from custom_pyqt import CityGMLQTDialog
from MapInfo.Types import MapInfoDictionary

# redirect python stdio to Pro
sys.stdout = sys.stderr = sys.stdin = MessageOutput()


# TODO: change your addin class name here.
class MyAddin():
    def __init__(self, imapinfopro, thisApplication):
        try:
            # initiaize qt application
            self._qtapp = QApplication(sys.argv)
            self._pro = imapinfopro
            self._newButton = None
            self._thisApplication = thisApplication
            # Create A new Ribbon Tab and Add controls.
            self.AddButtonHomeToRibbon()
        except Exception as e:
            print("Failed to load: {}".format(e))

    def AddButtonHomeToRibbon(self):
        homeTab = self._pro.Ribbon.Tabs["TabHome"]
        if homeTab:
            tabGroup = homeTab.Groups["HomeFile"]
            if tabGroup:
                self._newButton = tabGroup.Controls.Add("Open3dSurface", "Open 3d Surface")
                if self._newButton:
                    self._newButton.IsQatItem = False
                    self._newButton.IsToggle = False
                    self._newButton.IsSelected = False
                    self._newButton.IsLarge = True
                    self._newButton.KeyTip = "OS"
                    self._newButton.Command = AddinUtil.create_command(self.on_open_dialog_qt_click, None)
                    self._newButton.KeyGesture = "Alt+Shift+S"
                    self._newButton.LargeIcon = CommonUtil.path_to_uri(
                        "pack://application:,,,/MapInfo.StyleResources;component/Images/Mapping/new3DMap_32x32.png")
                    self._newButton.SmallIcon = CommonUtil.path_to_uri(
                        "pack://application:,,,/MapInfo.StyleResources;component/Images/Mapping/new3DMap_16x16.png")
                    self._newButton.ToolTip = AddinUtil.create_tooltip("Open 3d Surfaces", "Open 3d Surfaces",
                                                                       "Always Enabled.")

    def on_open_dialog_qt_click(self, sender):
        try:
            vFile = MapInfoDictionary[String, Object]()
            vFile['Name'] = 'File'
            vFile['Type'] = 'File'
            vFile['Prompt'] = '_File:'
            vFile['Extension'] = 'GML'

            lods = List[String]()
            lods.Add('Auto')
            lods.Add('0')
            lods.Add('1')
            lods.Add('2')
            lods.Add('3')
            lods.Add('4')
            vValues = MapInfoDictionary[String, Object]()
            vValues['Name'] = 'LOD'
            vValues['Type'] = 'List'
            vValues['Prompt'] = 'LOD:'
            vValues['Value'] = 'Auto'
            vValues['Values'] = lods

            vLogical = MapInfoDictionary[String, Object]()
            vLogical['Name'] = 'FORCE'
            vLogical['Type'] = 'Logical'
            vLogical['Prompt'] = 'Force Conversion:'
            vLogical['Value'] = 'False'

            variables = List[MapInfoDictionary[String, Object]]()
            variables.Add(vFile)
            variables.Add(vValues)
            variables.Add(vLogical)

            if self._pro.Input('Input Special', variables, None):
                # for v in variables:
                #     print('{} {}'.format(v['Prompt'], v['Value']))
                proHwnd = self._pro.MainHwnd.ToInt32()
                qtdlg = CityGMLQTDialog(pro=self._pro, city_gml_file=vFile['Value'], lod=vValues['Value'],
                                        force=bool(vLogical['Value']))

                qtdlg.showDialog(proHwnd)
        except Exception as e:
            print("Error: {}".format(e))

    def unload(self):
        if self._newButton:
            homeTab = self._pro.Ribbon.Tabs["TabHome"]
            if homeTab:
                tabGroup = homeTab.Groups["HomeFile"]
                if tabGroup:
                    tabGroup.Controls.Remove(self._newButton)

        if self._qtapp:
            self._qtapp.exit()

        self._qtapp = None
        self._newButton = None
        self._thisApplication = None
        self._pro = None


# this class is needed with same name in order to load the python addin and can be copied 
# as it is when creating another addin.
class main():
    def __init__(self, imapinfopro):
        # imapinfopro is the object of type MapInfo.Type.IMapInfoPro 
        # giving access to the current running instance of MapInfo Pro.
        self._imapinfopro = imapinfopro

    def load(self):
        try:
            # uncomment these lines to debug the python script using VSCODE
            # Install ptvsd package into your environment using "pip install ptvsd"
            # Debug in VSCODE with Python: Attach configuration

            # ptvsd.enable_attach()
            # ptvsd.wait_for_attach()
            # ptvsd.break_into_debugger()

            # here initialize the addin class
            if self._imapinfopro:
                # obtain the handle to current mbx application
                thisApplication = self._imapinfopro.GetMapBasicApplication(os.path.splitext(__file__)[0] + ".mbx")
                self._addin = MyAddin(self._imapinfopro, thisApplication)
        except Exception as e:
            print("Failed to load: {}".format(e))

    def unload(self):
        try:
            if self._addin:
                self._addin.unload()
                del self._addin
            self._addin = None
        except Exception as e:
            print("Failed to unload: {}".format(e))

    def __del__(self):
        self._imapinfopro = None
        pass

    # optional -- tool name that shows in tool manager
    def addin_name(self) -> str:
        # TODO: change here
        return "Python Add-in"

    # optional -- description that shows in tool manager
    def addin_description(self) -> str:
        # TODO: change here
        return "Python Add-in Description"

    # optional -- default command text in  tool manager
    def addin_defaultcommandtext(self) -> str:
        # TODO: change here
        return "Python Add-in Default Command"

    # optional -- default command when run or double-clicked in tool manager
    def addin_defaultcommand(self):
        # TODO: change here
        self.on_default_button_clicked(self)

    # optional -- image that  shows in tool manager
    def addin_imageuri(self) -> str:
        # TODO: change here
        return "pack://application:,,,/MapInfo.StyleResources;component/Images/Application/about_32x32.png"

    def on_default_button_clicked(self, sender):
        # TODO: change here
        try:
            print('default command executed')
        except Exception as e:
            print("Failed to execute: {}".format(e))
