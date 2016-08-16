

"""
This is a GUI for the QSSPL system. It interfaces with USB6356 NI DAQ card.
Currently it is assumed that the NI card is Dev3, and it reads three channels
and outputs on 1. This could all be changed, but i'm not sure why I want to
yet.

    To use this the NI drives need to be installed!

Things to improve:

    Definition of Dev/ and channels
    Selectable inputs and output voltage ranges.
    Make that you can't load incorrect values (int and floats at least)
"""

from gui.gui import MainWindow
from PyQt5 import QtCore, QtWidgets, QtGui
import sys


def main():

    qApp = QtWidgets.QApplication(sys.argv)
    aw = MainWindow()
    sys.exit(qApp.exec_())


if __name__ == "__main__":
    main()
