import numpy as np
import pandas as pd
import pyqtgraph as pg
import os
from PyQt5.QtCore import *
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import trace_objects as to
import pyqt_objects as po


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        print("Initializing Window")
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        # self.filename = "C://Users//peaq//Uniarbeit//Python//Manual_Pyeakfitter//_result_no_masslist.hdf5"
        self.filename = None
        self.savefilename = None
        self.file_loaded = False
        self.init_Ui_file_not_loaded()



    def init_Ui_file_not_loaded(self):
        self.centralwidget = QtWidgets.QWidget(self)
        # main layout setup
        self.overallverticallayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.verticalLayout1 = QtWidgets.QVBoxLayout()  #layout on the left with the masslist, and other stuff
        self.verticalLayout2 = QtWidgets.QVBoxLayout()  #laout on the right with the graph
        self.jump_to_mass_layout = QtWidgets.QHBoxLayout()
        self.jump_to_compound_layout = QtWidgets.QHBoxLayout()


        self.horizontalLayout.addLayout(self.verticalLayout1)
        self.horizontalLayout.addLayout(self.verticalLayout2)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1,7)
        self.verticalLayout1.addLayout(self.jump_to_mass_layout)
        self.verticalLayout1.addLayout(self.jump_to_compound_layout)

        # plot widget for the verticalLayout2
        self.graphWidget = pg.PlotWidget()
        axis = pg.DateAxisItem()
        self.graphWidget.setAxisItems({'bottom': axis})
        self.verticalLayout2.addWidget(self.graphWidget)

        # list of masses
        self.masslist_widget = to.QlistWidget_Msasslist(self,[],[])

        self.label_jump_mass = QtWidgets.QLabel("Jump to mass: ")
        self.jump_to_mass_input = QtWidgets.QLineEdit()
        self.jump_to_mass_input.setValidator(QtGui.QDoubleValidator(0., 500., 4))
        self.label_jump_compound = QtWidgets.QLabel("Jump to compound: ")
        self.jump_to_compound_input = QtWidgets.QLineEdit()
        self.jump_to_compound_button = QtWidgets.QPushButton("OK")
        self.jump_to_mass_layout.addWidget(self.label_jump_mass)
        self.jump_to_mass_layout.addWidget(self.jump_to_mass_input)
        self.jump_to_compound_layout.addWidget(self.label_jump_compound)
        self.jump_to_compound_layout.addWidget(self.jump_to_compound_input)
        self.jump_to_compound_layout.addWidget(self.jump_to_compound_button)

        # create menu
        menubar = QtWidgets.QMenuBar()
        self.actionFile = menubar.addMenu("File")
        # the po.openfile triggers init_UI_file_loaded() and init_plots()
        openfile = QtWidgets.QAction("Open", self)
        openfile.setShortcut("Ctrl+O")
        openfile.triggered.connect(self.open_file)
        self.actionFile.addAction(openfile)


        self.actionFile.addSeparator()
        quit = QtWidgets.QAction("Quit", self)
        quit.setShortcut("Alt+F4")
        quit.triggered.connect(lambda: sys.exit(0))
        self.actionFile.addAction(quit)

        self.settingsMenubar = menubar.addMenu("Settings")
        self.plotsettings_button = QtWidgets.QAction("Plot Settings", self)
        self.settingsMenubar.addAction(self.plotsettings_button)


        self.overallverticallayout.addWidget(menubar)
        self.overallverticallayout.addLayout(self.horizontalLayout)
        self.verticalLayout1.addWidget(self.masslist_widget)

        self.setCentralWidget(self.centralwidget)

    def open_file(self):
        # show the dialog
        dialog = QtWidgets.QFileDialog()
        filepath, filter = dialog.getOpenFileName(None, "Window name", "", "HDF5_files (*.hdf5)")
        self.filename = filepath
        # if self.file_loaded:
        #     print("remove old plot stuff")
        #     pyqtgraph_objects.remove_all_plot_items(parent)
        self.init_basket_objects()
        self.init_UI_file_loaded()
        self.init_plots()
        self.file_loaded = True

    def init_basket_objects(self):
        #those are the "basket" objects, where the data is in sp = all data that has to do with the spectrum, ml = all data to the masslist

        self.plot_settings = {"vert_lines_color_suggestions": (97, 99, 102,70),
                              "vert_lines_color_masslist": (38, 135, 20),
                              "vert_lines_color_masslist_without_composition": (13, 110, 184),
                              "vert_lines_color_isotopes": (252, 3, 244, 70), # RGB tubel and last number gives the transparency (from 0 to 255)
                              "vert_lines_width_suggestions": 1,
                              "vert_lines_width_masslist": 2,
                              "vert_lines_width_isotopes": 1.5,
                              "average_spectrum_color" : (252, 49, 3),
                              "max_spectrum_color": (122, 72, 6, 80),
                              "min_spectrum_color": (11, 125, 191, 80),
                              "sub_spectrum_color": (103, 42, 201, 80),
                              "color_cycle": ['r', 'g', 'b', 'c', 'm', 'y'],
                              "current_color": 0,
                              "background_color": "w",
                              "show_plots": [True,False,False,False], #plots corresponding to [avg spectrum, min spec, max spect, subspectr]
                              "avg": False,
                              "raw": True
                              }
        self.tr = to.Traces(self.filename,useAveragesOnly=self.plot_settings["avg"], Raw=self.plot_settings["raw"])
        self.tr.update_Traces(np.array([19.017856,  21.022096,  27.022936]))
        self.spectrumplot = []
        self.spectrum_max_plot = []
        self.spectrum_min_plot = []
        self.subspec_plot = []
        self.jumping_possible = True


    def init_UI_file_loaded(self):
        #add functionality to:
        #slider
        # masslist shown on left
        self.masslist_widget.redo_qlist(self.tr.MasslistMasses, self.tr.MasslistCompositions)
        self.masslist_widget.itemChanged.connect(self.masslist_tick_changed)
        self.masslist_widget.itemClicked.connect(self.jump_to_mass)
        #jump to mass widget
        self.jump_to_mass_input.textChanged.connect(self.jump_to_mass)
        self.jump_to_compound_button.pressed.connect(lambda: self.jump_to_compound(self.jump_to_compound_input.text()))
        self.jump_to_compound_input.returnPressed.connect(lambda: self.jump_to_compound(self.jump_to_compound_input.text()))
        #menubar stuff

        self.plotsettings_window = po.PlotSettingsWindow(self)
        self.plotsettings_button.triggered.connect(self.plotsettings_window.show)


    def init_plots(self):
        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        self.graphWidget.setBackground(self.plot_settings["background_color"])
        self.graphWidget.setLabel('bottom', "Time")
        self.graphWidget.setLabel('left', "Signal [cps]")
        self.graphWidget.setLogMode(y=True)
        self.graphWidget.addLegend()
        # make bg plots
        # pyqtgraph_objects.replot_spectra(self,self.plot_settings["show_plots"])
        self.update_plots()
        # set the restrictions on the movement
        self.vb = self.graphWidget.getViewBox()
        self.vb.autoRange()
        self.vb.setMenuEnabled(False)
        self.vb.setAspectLocked(lock=False)
        self.vb.setAutoVisible(y=1.0)
        self.vb.setMouseEnabled(x=True, y=False)   # restric movement
        self.vb.enableAutoRange(axis='y', enable=True)
        # when xrange changed make the following
        # to signals and slots: https://www.tutorialspoint.com/pyqt/pyqt_signals_and_slots.htm#:~:text=Each%20PyQt%20widget%2C%20which%20is,%27%20to%20a%20%27slot%27.
        self.vb.sigXRangeChanged.connect(lambda: self.on_xlims_changed(self.vb))

    def masslist_tick_changed(self):
        self.masslist_widget.tick_changed()
        self.tr.update_Traces(self.masslist_widget.currentmasses)
        self.update_plots()
        self.vb.autoRange()

    def remove_all_plot_items(self):
        """remove all plot_items in the graphWidget

        Parameters
        ----------
        parent: object
            Mainwindow object where the Line are stored

        Returns
        -------
        None
        """
        # used: https://www.geeksforgeeks.org/pyqtgraph-getting-all-child-items-of-graph-item/
        for item in self.graphWidget.allChildItems():
            self.graphWidget.removeItem(item)

    def on_xlims_changed(self, viewbox):
        # for a similar examples look at:
        # import pyqtgraph.examples
        # pyqtgraph.examples.run()
        # InfiniteLine Example
        #documentation https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/infiniteline.html
        pass
    #     xlims, ylims = viewbox.viewRange()
    #     # print("xlims changed ", xlims, np.diff(xlims))
    #
    #     if np.diff(xlims) > 1.1:
    #         pyqtgraph_objects.remove_all_vlines(self)
    #     else:
    #         pyqtgraph_objects.redraw_vlines(self, xlims)
    #     if np.diff(xlims) < 0.7:
    #         # only if we are shure, that we have the influence of only one peak we draw the local fit
    #         def to_worker():
    #             pyqtgraph_objects.redraw_localfit(self,xlims)
    #         worker = Worker(to_worker)
    #         self.threadpool.start(worker)

    def update_plots(self):
        # set the restrictions on the movement
        self.remove_all_plot_items()
        for (trace,composition) in zip(self.tr.Traces,self.masslist_widget.currentcompositions):
            current_color = self.plot_settings["color_cycle"][self.plot_settings["current_color"]]
            print("color",current_color)
            print(to.get_names_out_of_element_numbers(composition))
            self.spectrumplot = self.graphWidget.plot(self.tr.Times, trace,
                                                  pen=pg.mkPen(current_color),
                                                  name=to.get_names_out_of_element_numbers(composition))
            if self.plot_settings["current_color"] < len(self.plot_settings["color_cycle"])-1:
                self.plot_settings["current_color"] += 1
            else: self.plot_settings["current_color"] = 0
        self.plot_settings["current_color"] = 0
    def jump_to_mass(self, event):
        pass
        # if type(event) is str:
        #     mass = float(event)
        # elif type(event) is float:
        #     mass = event
        # else:
        #     mass, compoundstr = event.text().rsplit('  ', 1)
        #     mass = float(mass)
        # print("jump to mass: ", mass)
        # xlims, ylims = self.vb.viewRange()
        # xrange = xlims[1] - xlims[0]
        # target_mass = mass
        # newxlims = (target_mass - xrange/2 , target_mass + xrange/2)
        # self.vb.setXRange(*newxlims, padding = 0)

    def jump_to_compound(self,compoundstring):
        pass
        # mass, compound = mo.get_element_numbers_out_of_names(compoundstring)
        # self.jump_to_mass(float(mass))
        # if not (self.ml.suggestions.element_numbers == compound).all(axis=1).any():
        #     self.ml.add_suggestion_to_sugglist(self, compound)



    def keyPressEvent(self, event):
        if event.key() == Qt.Key_D:
            xlims, ylims = self.vb.viewRange()
            self.vb.setXRange(xlims[0] +1 , xlims[1] + 1, padding = 0)
        if event.key() == Qt.Key_A:
            xlims, ylims = self.vb.viewRange()
            self.vb.setXRange(xlims[0] - 1, xlims[1] - 1, padding = 0)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys._excepthook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        print("silent error")
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
