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
        QtCore.QAbstractTableModel.__init__(self, parent = None)

        self._listNodes = None
        self._headers = None

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

        if role == QtCore.Qt.CheckStateRole and column == 4:
            if self._listNodes[row][column]:
                return QtCore.Qt.Checked
            else:
                return QtCore.Qt.Unchecked

        if role == QtCore.Qt.DisplayRole:
            try:
                value = self._listNodes[row][column]
                return value
            except:
                pass

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()

        if order == QtCore.Qt.DescendingOrder:
            orderState = True
        else:
            orderState = False

        self._listNodes = sorted(self._listNodes, key = operator.itemgetter(column), reverse = orderState)

        self.layoutChanged.emit()

if __name__ == "__main__":
    import random
    import sys

    class FakeBBox():
        def __init__(self):
            self.w = int(random.randrange(0, 2048))
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

    # testing code
    table = QtGui.QTableView()
    table.setSelectionBehavior(QtGui.QTableView.SelectRows)
    table.setSortingEnabled(True)
    table.show()
    table.setModel(model)

    sys.exit(app.exec_())
