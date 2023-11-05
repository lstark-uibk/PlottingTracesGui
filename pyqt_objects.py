from PyQt5.QtWidgets import QMainWindow
class PlotSettingsWindow(QMainWindow):
    def __init__(self, parent=None):
        pass
        # super(PlotSettingsWindow, self).__init__(parent)
        # self.centralWidget = QtWidgets.QWidget(self)
        # self.centralLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        # self.parent = parent
        #
        # # here I have to use a checkbox not a radiobutton because radionbuttons are exclusively only one on
        # Checkbox = QtWidgets.QCheckBox("Show Min/Max Spectrum")
        # Checkbox.setChecked(False)
        # Checkbox.stateChanged.connect(lambda: self.onClick([1,2]))
        # self.centralLayout.addWidget(Checkbox)
        #
        # Checkbox1 = QtWidgets.QCheckBox("Show Subspectra")
        # Checkbox1.setChecked(False)
        # Checkbox1.stateChanged.connect(lambda: self.onClick([3]))
        #
        # self.centralLayout.addWidget(Checkbox1)
        # self.setCentralWidget(self.centralWidget)

    def onClick(self, index):
        pass
        # if self.parent.file_loaded:
        #     checkbox = self.sender()
        #     if checkbox.isChecked():
        #         for i in index:
        #             self.parent.plot_settings["show_plots"][i] = True
        #     if not checkbox.isChecked():
        #         for i in index:
        #             self.parent.plot_settings["show_plots"][i] = False
        #     # print(self.parent.plot_settings["show_plots"])
        #     pyqtgraph_objects.replot_spectra(self.parent,self.parent.plot_settings["show_plots"])
