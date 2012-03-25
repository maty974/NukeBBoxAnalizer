'''
Created on Mar 25, 2012

@author: maty974
@contact: matthieu.cadet@gmail.com
@summary: 
'''

from PySide import QtCore, QtGui
import sys

class NodesTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent = None)

        self._listNodes = []
        self._headers = ["Name", "Class", "Width", "Height", "Cropped", "Label"]

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
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()

            try:
                nodeName = self._listNodes[row][column]
                return nodeName
            except:
                pass


if __name__ == "__main__":
    class FakeBBox():
        def __init__(self):
            self.w = 100
            self.h = 200

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
        pseudoList.append([node.name() + ":%s" % i, node.Class(), node.bbox().w, node.bbox().h, False])

    app = QtGui.QApplication(sys.argv)

    # nodeListModel
    model = NodesTableModel()
    model._listNodes = pseudoList

    # testing code
    table = QtGui.QTableView()
    table.setSelectionBehavior(QtGui.QTableView.SelectRows)
    table.show()
    table.setModel(model)

    sys.exit(app.exec_())
