#! python3.5
import os
from collections import OrderedDict
from PyQt5 import QtCore, QtWidgets, QtGui

import core
import sys
import traceback

from glob import glob
from semiconductor.recombination.intrinsic import Auger, Radiative
from semiconductor.electrical import Mobility
from semiconductor.material import IntrinsicCarrierDensity, BandGapNarrowing

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


class input_box(QtWidgets.QLineEdit):

    def __init__(self):
        super().__init__('Unchanged')


class input_combo(QtWidgets.QComboBox):

    def __init__(self, List):
        super().__init__()
        self.addItems(List)
        # self.addItems(['Unchanged'])
        # self.setCurrentText('Unchanged')


class optional_input_widgets():

    class_dic = {'QLineEdit': input_box,
                 'QComboBox': input_combo,
                 }

    index = 0

    var_name_dic = {}

    def __init__(self):
        # super().__init__()

        # if parent is not None:
        #     self.setParent(parent)

        self.grid = QtWidgets.QGridLayout()

    def add_item(self, label_name, vairable_name, Q_type, *args):
        label = QtWidgets.QLabel(label_name + ':')

        self.grid.addWidget(label, self.index, 0)

        input_item = self.class_dic[Q_type](*args)
        input_item.vairable_name = vairable_name
        self.grid.addWidget(input_item, self.index, 1)

        self.index += 1

    def get_settings(self, dic, parent):
        # print(self.var_name_dic.keys())
        for inputbox in parent.findChildren(QtWidgets.QLineEdit):
            key = inputbox.vairable_name
            text = inputbox.text()
            if text != 'Unchanged':
                dic[key] = float(text)

        for combobox in parent.findChildren(QtWidgets.QComboBox):
            key = combobox.vairable_name
            text = combobox.currentText()
            if text != 'Unchanged':
                dic[key] = text
                print(key, text)

        return dic


class _optional_settings(QtWidgets.QWidget):
    settings = {}

    def __init__(self, parent=None):
        super().__init__()

        if parent is not None:
            self.setParent(parent)
        self.initUI()

    def initUI(self):

        self.widgets = optional_input_widgets()

        self.widgets.add_item('Thickness (um)', 'thickness', 'QLineEdit')
        self.widgets.add_item(r'Doping (cm<sup>-3</sup>)',
                              'doping', 'QLineEdit')
        self.widgets.add_item('Optical constant (38 mA cm<sup>-2</sup>)',
                              'optical_constant', 'QLineEdit')
        self.widgets.add_item('MCD (cm<sup>-3</sup>)',
                              'nxc_fit_center', 'QLineEdit')
        self.widgets.add_item('Fit range (0-1)', 'fitting_width', 'QLineEdit')

        # now add the combo boxes
        self.widgets.add_item('Doping type', 'dopant_type',
                              'QComboBox', ['Unchanged', 'p-type', 'n-type'])
        self.widgets.add_item('Intrinsic carrier concentration model',
                              'ni', 'QComboBox', IntrinsicCarrierDensity().available_models())
        self.widgets.add_item('Auger model', 'auger',
                              'QComboBox', Auger().available_models())
        self.widgets.add_item('Radiative model', 'radiative',
                              'QComboBox', Radiative().available_models())
        self.widgets.add_item('Mobility model', 'mobility_sum',
                              'QComboBox', Mobility().available_models())
        self.widgets.add_item('Band gap narrowing model', 'ni_eff',
                              'QComboBox', BandGapNarrowing().available_models())

        self.setLayout(self.widgets.grid)

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

    def get_settings(self, dic):

        return self.widgets.get_settings(dic, self.parent())


class Settings(QtWidgets.QWidget):

    use_sinton_values = True  # A flag that lets you use sinton or own calcs

    def __init__(self, parent=None):
        super().__init__()

        if parent is not None:
            self.setParent(parent)
        self.initUI()

    def initUI(self):
        grid = QtWidgets.QGridLayout()

        # A check box to use the stuffs
        check_box = QtWidgets.QCheckBox(
            "Use values from spreadsheet")
        check_box.setChecked(True)
        check_box.stateChanged.connect(self.default_values)

        self.others = _optional_settings()
        grid.addWidget(check_box)
        grid.addWidget(self.others)

        self.others.setHidden(True)
        self.setLayout(grid)

    def default_values(self):
        '''
        Checks if we should use the default values
        If, we should not, hides the appropriate part of the gui.
        '''
        sender = self.sender()
        if sender.isChecked():
            self.others.setHidden(True)
            self.use_sinton_values = True
        else:
            self.others.setVisible(True)

            self.use_sinton_values = False

        self.adjustSize()
        self.parentWidget().adjustSize()

        # self.setLayout(self.layout)

    def get_settings(self):

        dic = {}
        dic['use_sinton_values'] = self.use_sinton_values

        if not self.use_sinton_values:

            dic = self.others.get_settings(dic)

        return dic


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
        self.analysis_dic[
            "Kimmerle's carrier profile correction"] = ['Kimmerle_Diffusion']
        self.analysis_dic['Run all'] = [
            ''.join(value) for value in self.analysis_dic.values()]

        if parent is not None:
            self.setParent(parent)

        # put in an option to do them all

        self.initUI()

    def initUI(self):

        vbox = QtWidgets.QVBoxLayout()

        J0_det_label = QtWidgets.QLabel('J0 determination:')
        self.anaylsis_combo = QtWidgets.QComboBox(self)
        for option in self.analysis_dic.keys():
            self.anaylsis_combo.addItem(option)

        optin_combo_label = QtWidgets.QLabel('Analysis type:')
        self.MCD_optin_combo = QtWidgets.QComboBox(self)
        for option in ['At fixed MCD', 'At each MCD']:
            self.MCD_optin_combo.addItem(option)

        load_files_button = QtWidgets.QPushButton('Load files')
        load_folder_button = QtWidgets.QPushButton('Load folder')
        self.loaded_files_label = QtWidgets.QLabel('No files loaded:')
        self.loaded_FileNames = QtWidgets.QLineEdit('No files selected')

        load_files_button.clicked.connect(self.load_files)
        load_folder_button.clicked.connect(self.load_folder)
        self.anaylsis_combo.currentIndexChanged.connect(self._set_analysis)

        vbox.addWidget(load_files_button)
        vbox.addWidget(load_folder_button)
        vbox.addWidget(self.loaded_files_label)
        vbox.addWidget(self.loaded_FileNames)

        vbox.addWidget(J0_det_label)
        vbox.addWidget(self.anaylsis_combo)
        vbox.addWidget(optin_combo_label)
        vbox.addWidget(self.MCD_optin_combo)

        QtWidgets.QFileDialog()

        self.setLayout(vbox)

        # self.analysis = self.anaylsis_combo.currentText()

    def _set_analysis(self, int):

        self.analysis_method = self.analysis_dic[
            self.anaylsis_combo.currentText()]
        pass

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
            self.loaded_FileNames.setText('Selected a file\s or a folder')

        self.loaded_files_label.setText(
            '{0} files selected:'.format(len(self.files)))

        pass

    def get_settings(self):
        dic = {}
        dic['analysis_method'] = self.analysis_dic[
            self.anaylsis_combo.currentText()]
        dic['files'] = self.files
        dic['analysis_MCD'] = self.MCD_optin_combo.currentText()

        return dic


class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()
        self._dir = os.getcwd()

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

    @property
    def directory(self):
        if len(self.analysis.files) == 0:
            _dir = self._dir
        else:
            _dir = os.path.dirname(self.analysis.files[0])

        return _dir

    @directory.setter
    def directory(self, value):
        self._dir = value

    def go(self):
        try:
            a.get()
            setting_dic = self.settings.get_settings()
            analysis_dic = self.analysis.get_settings()

            save_name, save_name_filter = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save your data dude', directory=self.directory, filter='csv (*.csv)')

            if save_name != '' and save_name_filter != '':
                data = core.data_handeller(
                    setting_dic, analysis_dic).go(save_name)

        except Exception as e:
            # print(str(e), traceback.print_exc())
            # print(type(err))
            with open('log.txt', mode='a') as f:
                traceback.print_exc(file=f)
                f.write(+ str(e))
            sys.exit(0)
        pass
