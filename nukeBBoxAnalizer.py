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
        self._maxBBoxWidth = 1920
        self._maxBBoxHeight = 1080

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

    @property
    def listNodes(self):
        return self._listNodes

    @listNodes.setter
    def listNodes(self, listInput):
        self._listNodes = listInput
        self._listNodes.modelParent = self

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
            return len(self.listNodes.list)
        except:
            return 0

    def data(self, index, role):
        row = index.row()
        column = index.column()
        headerName = self._headers[column]

        if column < len(self._listNodes.row(row)):
            value = self._listNodes.row(row)[column]
        else:
            value = ""

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignHCenter

        if role == QtCore.Qt.DisplayRole:
            return value

        if role == QtCore.Qt.BackgroundRole:
            if headerName == "Width (bbox)" and value > self.maxBBoxWidth or \
            headerName == "Height (bbox)" and value > self.maxBBoxHeight:
                return QtGui.QBrush(QtGui.QColor("#8F2B2B"))

    def sort(self, column, order):
        # TODO: maybe there is another way to do sorting here
        self.layoutAboutToBeChanged.emit()

        if order == QtCore.Qt.DescendingOrder:
            orderState = True
        else:
            orderState = False

        self._listNodes = sorted(self._listNodes, key = operator.itemgetter(column), reverse = orderState)

        self.layoutChanged.emit()

class NodesTableView(QtGui.QTableView):
    # TODO: maybe also add the node.width/height() image size
    _headers = ["Name", "Class", "Width (bbox)", "Height (bbox)", "Disabled", "Label"]

    def __init__(self, parent = None):
        QtGui.QTableView.__init__(self, parent)

        self.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.model = NodesTableModel()
        self.model.setHeaders(self._headers)

        self.proxyModel = QtGui.QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setSourceModel(self.model)

        self.setModel(self.proxyModel)
        self.show()

class NodesList():
    # TODO: self.addNode must be re-think... maybe use a dict
    # TODO: add a remove node
    # TODO: add a nuke.callback to update list on Node in DAG changed,deleted,added,...

    _ignoredNodeClass = ["BackdropNode", "Viewer", "Axis2", "Camera", "FillMat",
                         "ReadGeo2", "Scene", "Sphere", "TransformGeo", "Axis"]

    def __init__(self, data = []):
        self.modelParent = None
        self._nodeList = []
        self._rowList = []

    @property
    def rowList(self):
        return self._rowList

    @property
    def list(self):
        return self._nodeList

    def addNode(self, item):
        if item:
            if item not in self._nodeList and \
            item.Class() not in self._ignoredNodeClass:
                self._nodeList.append(item)

        self.notifyChanged()

    def row(self, index):
        return self.itemRowList(self._nodeList[index])

    def itemRowList(self, item):
        itemRow = [item.name(),
                   item.Class(),
                   item.bbox().w(),
                   item.bbox().h(),
                   item.knob("disable").value(),
                   item.knob("label").value() ]

        return itemRow

    def setRowList(self):
        for item in self._nodeList:
            itemRow = self.itemRowList(item)
            if itemRow not in self._rowList:
                self._rowList.append(itemRow)

        return self._rowList

    def removeNode(self, name):
        for node in self._nodeList:
            if node.name() == name:
                self._nodeList.remove(node)
                self.notifyChanged()
                break

    def notifyChanged(self):
        self.setRowList()

        if self.modelParent != None:
            self.modelParent.layoutChanged.emit()

if __name__ == "__main__":
    import random
    import sys

    class FakeKnob():
        def __init__(self):
            self._randomDisable = random.choice([True, False])
            self._randomLabel = random.choice(["", "user label", "other label"])

        def value(self):
            if self.name == "disable":
                return self._randomDisable

            if self.name == "label":
                return self._randomLabel

    class FakeBBox():
        def __init__(self):
            self._randomWidth = int(random.randrange(0, 2160))
            self._randomHeight = int(random.randrange(0, 2048))

        def w(self):
            return self._randomWidth

        def h(self):
            return self._randomHeight

    class FakeNode():
        def __init__(self):
            self._randomClass = random.choice(["Grade", "ColorCorrect", "Merge", "Blur", "DirBlurWrapper"])
            self.id = random.randint(0, 50)
            self._name = "nodeName_%s" % self.id
            self.bboxFake = FakeBBox()
            self.knobFake = FakeKnob()

        def bbox(self):
            return self.bboxFake

        def name(self):
            return self._name

        def Class(self):
            return self._randomClass

        def knob(self, name):
            self.knobFake.name = name
            return self.knobFake

    pseudoList = NodesList()
    for i in range(0, 6):
        node = FakeNode()
        pseudoList.addNode(node)

    app = QtGui.QApplication(sys.argv)
    app.setStyle("plastique")

    # tableView
    table = NodesTableView()
    table.model.listNodes = pseudoList

    # filter test
    #table.proxyModel.setFilterKeyColumn(1)
    #table.proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
    #table.proxyModel.setFilterWildcard("bl*")

    # test add other node after
    otherNode = FakeNode()
    otherNode._name = "otherNode"
    pseudoList.addNode(otherNode)

    # test remove node from list
    #pseudoList.removeNode("otherNode")

    sys.exit(app.exec_())
