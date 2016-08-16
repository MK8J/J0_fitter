#! python3.5
import sys
import os
from collections import OrderedDict
from PyQt5 import QtCore, QtWidgets, QtGui
import core
import IO
from glob import glob

# progname = os.path.basename(sys.argv[0])
# progversion = "0.1"


# class CustomWidget(QtGui.QLabel):
#     signal_hid = QtCore.pyqtSignal()
#     signal_shown = QtCore.pyqtSignal()
#
#     def hideEvent(self, event):
#         super(CustomWidget, self).hideEvent(event)
#         self.signal_hided.emit()
#
#     def showEvent(self, event):
#         super(CustomWidget, self).showEvent(event)
#         self.signal_shown.emit()


class _optional_settings(QtWidgets.QWidget):
    settings = {}

    def __init__(self, parent=None):
        super().__init__()

        if parent is not None:
            self.setParent(parent)
        self.initUI()

    def initUI(self):
        grid = QtWidgets.QGridLayout()

        names = ['thickness', 'doping', 'optical constant']
        positions = [(i, j) for i in range(1, 4) for j in range(1)]
        for position, name in zip(positions, names):

            label = QtWidgets.QLabel(name + ':')
            grid.addWidget(label, *position)

            text = QtWidgets.QLineEdit('default')
            self.settings[name] = text
            grid.addWidget(text, position[0], position[1] + 1)

        label = QtWidgets.QLabel('doping type:')
        grid.addWidget(label, position[0] + 1, 0)
        combo = QtWidgets.QComboBox(self)
        combo.addItem("p-type")
        combo.addItem("n-type")
        self.settings['doping type'] = combo

        grid.addWidget(combo, position[0] + 1, 1)

        self.setLayout(grid)

    def hide(self):
        sender = self.sender()
        sender.isHiden(True)

    def enable(self):

        sender = self.sender()

        if sender.checkState():
            state = False
        else:
            state = True

        for setting in self.settings.keys():
            self.settings[setting].setDisabled(state)

    def get_settings(self):
        dic = {}
        for key in self.settings.keys():
            try:
                dic[key] = self.settings[key].text()
            except:
                dic[key] = self.settings[key].currentText()

        return dic


class Settings(QtWidgets.QWidget):
    settings = {}

    def __init__(self, parent=None):
        super().__init__()

        if parent is not None:
            self.setParent(parent)
        self.initUI()

    def initUI(self):
        grid = QtWidgets.QGridLayout()

        # A check box to use the stuffs
        check_box = QtWidgets.QCheckBox(
            "Use defult spreadsheet values")
        check_box.setChecked(True)
        check_box.stateChanged.connect(self.enable)

        self.others = _optional_settings()
        grid.addWidget(check_box)
        grid.addWidget(self.others)
        self.setLayout(grid)

        print(self.children())

    def enable(self):
        self.others.isHiden(True)


class Analysis(QtWidgets.QWidget):
    '''
    A class to contain the paramters used for the analysis
    and get the files to be analysed

    This inlcudes file information, and analysis method
    '''
    files = []
    analysis_method = ['kane&swanson']

    def __init__(self, parent=None):
        super().__init__()

        # create an ordered dictionary
        self.analysis_dic = OrderedDict({})

        self.analysis_dic['Kane & Swanson'] = ['kane&swanson']
        self.analysis_dic["King's Auger correction"] = ['king']
        self.analysis_dic[
            "Kimmerle's Intrinsic carrier correction"] = ['Kimmerle_BGN']
        self.analysis_dic["Kimmerle's SRH"] = ['Kimmerle_SRH']
        # self.analysis_dic[
        #     "Kimmerle's carrier profile correction"] = ['Kimmerle_Diffusion']
        self.analysis_dic['Run all'] = [
            ''.join(value) for value in self.analysis_dic.values()]

        if parent is not None:
            self.setParent(parent)

        # put in an option to do them all

        self.initUI()

    def initUI(self):

        vbox = QtWidgets.QVBoxLayout()

        combo = QtWidgets.QComboBox(self)
        for option in self.analysis_dic.keys():
            combo.addItem(option)

        load_files_button = QtWidgets.QPushButton('Load files')
        load_folder_button = QtWidgets.QPushButton('Load folder')
        label = QtWidgets.QLabel('Files loaded:')
        self.loaded_FileNames = QtWidgets.QLineEdit('No files selected')

        load_files_button.clicked.connect(self.load_files)
        load_folder_button.clicked.connect(self.load_folder)
        combo.currentIndexChanged.connect(self._set_analysis)

        vbox.addWidget(load_files_button)
        vbox.addWidget(load_folder_button)
        vbox.addWidget(label)
        vbox.addWidget(self.loaded_FileNames)

        vbox.addWidget(combo)

        QtWidgets.QFileDialog()

        self.setLayout(vbox)

        self.analysis = combo.currentText()

    def _set_analysis(self, int):

        sender = self.sender()
        self.analysis_method = self.analysis_dic[sender.currentText()]

    def load_files(self, e):
        '''
        loads the selected files into the self.files list
        '''
        fname = QtWidgets.QFileDialog.getOpenFileNames(
            self, 'Select files dude', filter='*.xlsm')

        if fname[0]:
            self.files = fname[0]

        self._get_data_from_first_file()

    def load_folder(self, e):
        '''
        The action from load files
        '''
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Select a folder man')

        if fname[0]:
            self.files = glob(fname + os.sep + '*.xlsm')

        self._get_data_from_first_file()

    def _get_data_from_first_file(self):
        if len(self.files) > 0:
            string = '; '.join(
                os.path.split(fname)[-1] for fname in self.files)
            self.loaded_FileNames.setText(string)
        else:
            self.loaded_FileNames.setText('No files selected')

        pass

    def get_settings(self):
        dic = {}
        dic['analysis_method'] = self.analysis_method
        dic['files'] = self.files

        return dic


class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        vbox = QtWidgets.QVBoxLayout()

        self.settings = Settings(self)
        self.analysis = Analysis(self)

        go = QtWidgets.QPushButton('Go!')
        go.clicked.connect(self.go)

        vbox.addWidget(self.analysis)
        vbox.addWidget(self.settings)
        vbox.addWidget(go)

        self.setLayout(vbox)

        self.show()

    def go(self):

        setting_dic = self.settings.get_settings()
        analysis_dic = self.analysis.get_settings()

        data = core.data_handeller(setting_dic, analysis_dic).get_J0_nxc_scan()
        IO.save('test', data)

        pass
