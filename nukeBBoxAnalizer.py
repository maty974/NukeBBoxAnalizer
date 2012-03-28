'''
Created on Mar 25, 2012

@author: Matthieu Cadet
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
        self._maxBBoxWidth = 2048
        self._maxBBoxHeight = 1152

    @property
    def maxBBoxWidth(self):
        return self._maxBBoxWidth

    @maxBBoxWidth.setter
    def maxBBoxWidth(self, value):
        self._maxBBoxWidth = value
        self.layoutChanged.emit()

    @property
    def maxBBoxHeight(self):
        return self._maxBBoxHeight

    @maxBBoxHeight.setter
    def maxBBoxHeight(self, value):
        self._maxBBoxHeight = value
        self.layoutChanged.emit()

    def setListNodes(self, listInput):
        self._listNodes = listInput
        self.layoutChanged.emit()

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
        try:
            return len(self._listNodes)
        except:
            return 0

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
                return QtGui.QBrush(QtGui.QColor("#8F2B2B"))

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
    _headers = ["Name", "Class", "Width", "Height", "Cropped", "Label"]

    def __init__(self, parent = None):
        QtGui.QTableView.__init__(self, parent)

        self.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.model = NodesTableModel()
        self.model.setHeaders(self._headers)

        self.setModel(self.model)
        self.show()

class NodesList():
    _ignoredNodeClass = ["BackdropNode", "Viewer", "Axis2", "Camera", "FillMat",
                         "ReadGeo2", "Scene", "Sphere", "TransformGeo", "Axis"]

    def __init__(self, data = []):
        self._nodeList = []
        self._row = []

    def addNode(self, item):
        if item:
            if item not in self._nodeList and \
            item.Class() not in self._ignoredNodeClass:
                self._nodeList.append(item)

    def itemRowList(self, item):
        itemRow = [item.name(), item.Class(), item.bbox().w(), item.bbox().h(), False]
        return itemRow

    def getRowList(self):
        for item in self._nodeList:
            itemRow = self.itemRowList(item)
            if itemRow not in self._row:
                self._row.append(itemRow)

        return self._row

if __name__ == "__main__":
    import random
    import sys

    class FakeBBox():
        def w(self):
            return int(random.randrange(0, 2160))

        def h(self):
            return int(random.randrange(0, 2048))

    class FakeNode():
        def __init__(self):
            self.bbox = FakeBBox

        def name(self):
            return "nodeName"

        def Class(self):
            return "className"

    pseudoList = NodesList()
    for i in range(0, 6):
        node = FakeNode()
        pseudoList.addNode(node)

    app = QtGui.QApplication(sys.argv)
    app.setStyle("plastique")

    # tableView
    table = NodesTableView()
    table.model.setListNodes(pseudoList.getRowList())

    sys.exit(app.exec_())
