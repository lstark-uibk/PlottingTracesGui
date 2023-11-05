import numpy as np
import math
import h5py
import datetime
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtWidgets import QListWidgetItem, QListWidget
import pyqtgraph as pg
import re
class Traces():
    MasslistElements = ["C", "C13", "H", "H+", "N", "O", "O18", "S"]
    Order_of_letters = [0, 1, 2, 7, 4, 5, 6, 3]
    MasslistElementsMasses = np.array([12,
                                13.00335,
                                1.00783,
                                1.007276,
                                14.00307,
                                15.99492,
                                17.99916,
                                31.97207,
                               ])
    def __init__(self,Filename,useAveragesOnly=True,startTime = 0, endTime = 0,Raw = True):
        self.Times = []
        self.Timeindices = []
        self.MasslistMasses = []

        self.MasslistElements = []
        self.MasslistElementsMasses = []
        self.MasslistCompositions = []
        self.Traces = np.array([])
        self.filename = Filename
        self.starttime = startTime
        self.endtime = endTime
        self.useaveragesonly = useAveragesOnly
        self.raw = Raw
        self._init_information(self.filename,useAveragesOnly=useAveragesOnly)


    def _init_information(self, filename, useAveragesOnly = True, raw = False):
        self.filename = filename
        with h5py.File(self.filename, "r") as f:
            from_timestamp_vec = np.vectorize(lambda x: QDateTime.fromSecsSinceEpoch(int(round(x))))
            # self.Times = from_timestamp_vec(self.Times)
            print("Loading Masslist Information")
            #check time ordering
            self.MasslistMasses = f["MassList"][()]
            self.MasslistCompositions = f["ElementalCompositions"][()]
        print("loading Times")
        self.update_Times()
        print("loading Traces")
        self.update_Traces(massesToLoad = "none")
    def update_Times_Traces(self,massesToLoad = "none"):
        self.update_Times()
        self.update_Traces(massesToLoad)
    def update_Times(self):
        with h5py.File(self.filename, "r") as f:
            print("Loading Times:")
            if self.useaveragesonly:
                self.Times = f["AvgStickCpsTimes"][()]
            else:
                try:
                    self.Times = f["Times"][()]
                except:
                    print("Could not load high res time, maybe this is an average-only result file?")
                    return []
            if self.starttime < self.endtime:
                self.Timeindices = np.where((self.Times >= self.starttime) & (self.Times <= self.endtime))[0]
                self.Times = self.Times[self.Timeindices]
            else:
                self.Timeindices = np.where(np.full(self.Times.shape, True))[0]
        return self.Times

    def update_Traces(self, massesToLoad = "none"):
        """

        :param filename:
        :param massesToLoad: np.array[] if masseToLoad = "all" -> load all masses, if "none" -> no masses
        :param Timeindices:
        :param useAveragesOnly:
        :param raw:
        :return:
        """

        dsTexists = False
        filename = self.filename
        if isinstance(massesToLoad, np.ndarray) or isinstance(massesToLoad,(float,int)):
            Massestoloadindices = np.where(np.any((np.isclose(self.MasslistMasses[:, None], massesToLoad , rtol=1e-5, atol=1e-8)),axis=1))[0]
            if isinstance(massesToLoad,(float,int)):
                Massestoloadindices = int(Massestoloadindices)
            print(f"Loading Masses {massesToLoad}")
        else:
            if massesToLoad == "none":
                print("No Masses to load selected")
                return np.array([])
            elif massesToLoad == "all":
                print("Loading all Masses")
                Massestoloadindices = np.where(np.full(self.MasslistMasses.shape, True))
            else:
                print("Unknow Masses to Load")
                return np.array([])


        with h5py.File(filename, "r") as f:
            if self.useaveragesonly:
                self.Times = f["AvgStickCpsTimes"][()]
                print("Loading Average Traces")
                if self.raw:
                    print("Raw")
                    ds = f["AvgStickCps"]
                else:
                    print("Corrected")
                    ds = f["CorrAvgStickCps"]
            else:
                print("Loading high time resolution Traces")
                try:
                    self.Times = f["Times"][()]
                except:
                    print("Could not load high res time, maybe this is an average-only result file?")
                    return []
                if self.raw:
                    print("Raw")
                    if "StickCps" in f:
                        ds = f["StickCps"]
                    else:
                        print("No high time resolution available, is this a average only file?")
                        ds = f["AvgStickCps"]
                else:
                    if "CorrStickCps" in f:
                        print("Corrected")
                        ds = f["CorrStickCps"]
                    else:
                        print("No high time resolution available, is this a average only file?")
                        ds = f["CorrAvgStickCps"]
                    if "CorrStickCpsT" in f:
                        print("A transposed dataset for faster loading is available.")
                        dsT = f["CorrStickCpsT"]
                        dsTexists = True
                    else:
                        print(
                            "Transposed dataset for faster loading is NOT available. You can create one with ResultFileFunctions.transposeStickCps(filename).")

            if not dsTexists:
                self.Traces = ds[:,self.Timeindices][Massestoloadindices,:]
            else:
                self.Traces = dsT[self.Timeindices,:][:,Massestoloadindices]
            return self.Traces
            # get all the indices of massesToLoad



class QlistWidget_Masslist(QListWidget):
    def __init__(self, parent, Masses, Compositions):
        super().__init__(parent)
        self.masses = Masses
        self.compsitions = Compositions
        self.currentmasses = np.array([])
        self.currentcompositions = np.zeros((0, 8))
        self.load_on_tick = True


    def tick_changed(self):
        self.currentmasses = np.array([])
        self.currentcompositions = np.zeros((0, 8))

        for i in range(self.count()):
            item = self.item(i)
            state = item.checkState()
            if state == 2:
                self.currentmasses = np.append(self.currentmasses,self.masses[i])
                self.currentcompositions = np.append(self.currentcompositions, [self.compsitions[i,:]], axis=0)


    def redo_qlist(self,MasslistMasses,MasslistCompositions):
        '''Update the List on the right side of the Plot

        Parameters
        ----------
        qlist : QtWidgets.QListWidget

        Returns
        -------
        None
        '''
        self.masses = MasslistMasses
        self.compsitions = MasslistCompositions
        self.clear()
        for mass,element_numbers in zip(MasslistMasses, MasslistCompositions):
            item = QListWidgetItem(str(round(mass,6)) + "  " + get_names_out_of_element_numbers(element_numbers))
            item.setFlags(item.flags() | 1)  # Add the Qt.ItemIsUserCheckable flag
            item.setCheckState(0)  # 0 for Unchecked, 2 for Checked
            self.addItem(item)

    def check_multiple(self,lower, upper,parent):
        """

        :param checkstate: True or False
        :return:
        """
        self.load_on_tick = False
        for i in range(lower,upper):
            item = self.item(i)
            item.setCheckState(Qt.Checked)
            self.currentmasses = np.append(self.currentmasses, self.masses[i])
            self.currentcompositions = np.append(self.currentcompositions, [self.compsitions[i, :]], axis=0)
        self.load_on_tick = True

        parent.tr.update_Traces(self.currentmasses)
        parent.update_plots()


def get_names_out_of_element_numbers(compound_array):
    # only if any compounds are in compound array give a string
    '''Get the compound name out of a compound array

    Parameters
    ----------
    compound_array : np.array (nr_elements, nr_compounds)
        corresponding to the rules used in Masslist object

    Returns
    -------
    compoundname_list:
        str if compound_array is (nr_elements, 1)
            compound name
        list if (nr_elements, nr_compounds)
            compound names
    '''

    compoundname_list = []

    for compound in compound_array:
        if len(compound_array.shape) == 1:
            compound = compound_array
        if np.any(compound):
            order_of_letters = Traces.Order_of_letters
            names_elements = Traces.MasslistElements
            compoundletters = ""
            for index, order in enumerate(order_of_letters):
                # before the last letter (H+) add a " "
                if index == len(order_of_letters)-1:
                    compoundletters += " "
                if compound[order] == 0:
                    pass
                if compound[order] == 1:
                    compoundletters += names_elements[order]
                if compound[order] > 1:
                    compoundletters += names_elements[order] + str(round(compound[order]))
            compoundname_list.append(compoundletters)
            if len(compound_array.shape) == 1:
                return compoundletters
        else:
            if len(compound_array.shape) == 1:
                return ""
            compoundname_list.append("")

    return compoundname_list


def get_element_numbers_out_of_names(namestring):
    '''Get the compound name out of a compound array

    Parameters
    ----------
    namestring : str characters and numbers in any order

    Returns
    -------
    mass: float
        mass of the compound
    element_numbers: np.array (nr_elemets)


    '''
    ion = False
    if "+" in namestring:
        ion = True
        namestring = namestring.replace("+","")

    charlist = re.split(r'([a-zA-Z]\d+)|([a-zA-Z](?=[a-zA-Z]))', namestring)
    charlist = np.array([part for part in charlist if part],dtype="str")

    elements = np.array([""]*charlist.size, dtype = "str")
    numbers = np.zeros(charlist.size)
    for index, el_num in enumerate(charlist):
        if re.match(r'[a-zA-Z]\d', el_num):  # Character followed by a number
            splitted = re.split(r'([a-zA-Z])(\d+)',el_num)
            splitted = [part for part in splitted if part]
            element, number = splitted
            number = int(number)
            if element not in elements: #if the element is not already considered
                elements[index] = element
                numbers[index] = number
            else: #takes care of double writing eg C7H8NH4+
                numbers[element == elements] += number
        else:  # Character followed by another character
            if el_num not in elements: #if the element is not already considered
                elements[index] = el_num
                numbers[index] = 1
            else: #takes care of double writing eg C7H8NH4+
                numbers[el_num == elements] += 1


    if ion:
        elements = np.append(elements,"H+")
        numbers = np.append(numbers,1)
        number_H_mask = np.array([x.lower() for x in elements], dtype='str') == "h"
        if numbers[number_H_mask] > 0: # if the H number is more than 0
            numbers[number_H_mask] -= 1

    elementsinstring_lower = np.array([x.lower() for x in elements], dtype = 'str')

    names_elements = Traces.MasslistElements
    compound_array = np.array([0] * len(names_elements))
    for index,element in enumerate(names_elements):
        #make it lower, so that we have more freedom in writing
        element_lower = element.lower()
        if np.any(element_lower == elementsinstring_lower):
            compound_array[index] = numbers[element_lower == elementsinstring_lower]

    mass = np.sum(compound_array*Traces.MassElementsMasses)
    return mass, compound_array


