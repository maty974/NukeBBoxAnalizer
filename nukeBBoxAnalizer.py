'''
Created on Mar 25, 2012

@author: maty974
@contact: matthieu.cadet@gmail.com
@summary: 
'''

import operator
from PySide import QtCore, QtGui

class NodesTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)

        self._listNodes = None
        self._headers = None
        self._maxBBoxWidth = None
        self._maxBBoxHeight = None

    @property
    def maxBBoxWidth(self):
        return self._maxBBoxWidth

    @maxBBoxWidth.setter
    def maxBBoxWidth(self, value):
        self._maxBBoxWidth = value

    @property
    def maxBBoxHeight(self):
        return self._maxBBoxHeight

    @maxBBoxHeight.setter
    def maxBBoxHeight(self, value):
        self._maxBBoxHeight = value

    def setListNodes(self, listInput):
        self._listNodes = listInput

    def setHeaders(self, listInput):
        self._headers = listInput

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._headers[section]
            else:
                return section

    def columnCount(self, parent):
        return len(self._headers)

    def rowCount(self, parent):
        return len(self._listNodes)

    def data(self, index, role):
        row = index.row()
        column = index.column()
        headerName = self._headers[column]

        if column < len(self._listNodes[row]):
            value = self._listNodes[row][column]
        else:
            value = ""

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignHCenter

        if role == QtCore.Qt.CheckStateRole and headerName == "Cropped":
            if value:
                return QtCore.Qt.Checked
            else:
                return QtCore.Qt.Unchecked

        if role == QtCore.Qt.DisplayRole:
            if headerName == "Cropped":
                value = ""

            return value

        if role == QtCore.Qt.BackgroundRole:
            if headerName == "Width" and value > self.maxBBoxWidth or \
            headerName == "Height" and value > self.maxBBoxHeight:
                return QtGui.QBrush(QtGui.QColor("red"))

    def sort(self, column, order):
        # TODO: maybe there is another way to do sorting here
        self.layoutAboutToBeChanged.emit()

        if order == QtCore.Qt.DescendingOrder:
            orderState = True
        else:
            orderState = False

        # this exception is here because of the column Label cannot be sorted if
        # not all cell column contains value
        try:
            self._listNodes = sorted(self._listNodes, key = operator.itemgetter(column), reverse = orderState)
        except:
            pass

        self.layoutChanged.emit()

class NodesTableView(QtGui.QTableView):
    def __init__(self, parent = None):
        QtGui.QTableView.__init__(self, parent)

if __name__ == "__main__":
    import random
    import sys

    class FakeBBox():
        def __init__(self):
            self.w = int(random.randrange(0, 2160))
            self.h = int(random.randrange(0, 2048))

    class FakeNode():
        def __init__(self):
            self.bbox = FakeBBox

        def name(self):
            return "nodeName"

        def Class(self):
            return "className"

    pseudoList = []
    for i in range(0, 6):
        node = FakeNode()
        pseudoList.append([node.name() + ":%s" % i, node.Class(), node.bbox().w, node.bbox().h, True])

    app = QtGui.QApplication(sys.argv)
    app.setStyle("plastique")

    # nodeListModel
    headers = ["Name", "Class", "Width", "Height", "Cropped", "Label"]
    model = NodesTableModel()
    model.setHeaders(headers)
    model.setListNodes(pseudoList)
    model.maxBBoxWidth = 2048
    model.maxBBoxHeight = 1152

    # testing code
    table = QtGui.QTableView()
    table.setModel(model)
    table.setSelectionBehavior(QtGui.QTableView.SelectRows)
    table.setAlternatingRowColors(True)
    table.setSortingEnabled(True)
    table.sortByColumn(0, QtCore.Qt.AscendingOrder)
    table.show()

    sys.exit(app.exec_())
