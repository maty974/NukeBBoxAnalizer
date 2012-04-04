'''
Created on Mar 25, 2012

@author: Matthieu Cadet
@contact: matthieu.cadet@gmail.com
'''

# FIXME: MainWindow call with parent=None cause nuke crash on exit
# when the window is still opened

import operator
from PySide import QtCore, QtGui

__author__ = "Matthieu Cadet"
__maintainer__ = "Matthieu Cadet"
__email__ = "matthieu.cadet@gmail.com"
__copyright__ = "Copyright 2012"
__license__ = "?"
__version__ = "1.0"

class FilterWidget(QtGui.QHBoxLayout):
    def __init__(self, parent = None):
        QtGui.QHBoxLayout.__init__(self, parent)

        self.entry = QtGui.QLineEdit()
        self.type = QtGui.QComboBox()
        self.type.addItems(NodesTableView._headers)

        self.addWidget(self.type)
        self.addWidget(self.entry)

class InfosCountStatus(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(2, 2, 2, 2)

        labelFrameStyle = QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken

        label1 = QtGui.QLabel("total nodes: 0")
        label1.setFrameStyle(labelFrameStyle)

        label2 = QtGui.QLabel("oversize bbox: 0")
        label2.setFrameStyle(labelFrameStyle)

        hbox.addWidget(label1)
        hbox.addWidget(label2)

        hbox.setSizeConstraint(QtGui.QHBoxLayout.SetFixedSize)

        self.setLayout(hbox)

class MainWindow(QtGui.QDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle("Nuke BBox Analizer | %s" % __version__)
        self.resize(800, 600)

        self.filterGroup = QtGui.QGroupBox("Filter")
        self.filterWidget = FilterWidget()
        self.filterGroup.setLayout(self.filterWidget)

        QtCore.QObject.connect(self.filterWidget.entry, QtCore.SIGNAL("textChanged(QString)"), self.setFilter)
        QtCore.QObject.connect(self.filterWidget.type, QtCore.SIGNAL("currentIndexChanged(QString)"), self.setFilterColumn)

        self.nodeActionsGroup = QtGui.QGroupBox("Node Actions")
        self.displayOptionsGroup = QtGui.QGroupBox("Display Options")
        self.refreshButton = QtGui.QPushButton("Refresh")
        self.vboxLayout = QtGui.QVBoxLayout()
        self.vboxLayout.setContentsMargins(4, 4, 4, 4)
        self.hboxStatusBar = QtGui.QHBoxLayout()
        self.hboxBottomLayout = QtGui.QHBoxLayout()
        self.hboxTopLayout = QtGui.QHBoxLayout()

        self.tableView = NodesTableView()
        self.infosCountStatus = InfosCountStatus()

        self.hboxStatusBar.addWidget(self.infosCountStatus)
        self.hboxStatusBar.addWidget(self.refreshButton)

        self.vboxLayout.addLayout(self.hboxTopLayout)
        self.hboxTopLayout.addWidget(self.filterGroup)
        self.vboxLayout.addWidget(self.tableView)
        self.vboxLayout.addLayout(self.hboxBottomLayout)
        self.hboxBottomLayout.addWidget(self.nodeActionsGroup)
        self.hboxBottomLayout.addWidget(self.displayOptionsGroup)
        self.vboxLayout.addLayout(self.hboxStatusBar)

        self.setLayout(self.vboxLayout)

    def setFilterColumn(self, name):
        self.tableView.proxyModel.setFilterKeyColumn(self.tableView._headers.index(name))

    def setFilter(self, pattern):
        self.tableView.proxyModel.setFilterRegExp(pattern)

    def event(self, event):
        return QtGui.QWidget.event(self, event)

    def closeEvent(self, event):
        self.deleteLater()


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
            return len(self.listNodes)
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

        if role == QtCore.Qt.DisplayRole:
            return value

        if role == QtCore.Qt.BackgroundRole:
            if headerName == "Width (bbox)" and value > self.maxBBoxWidth or \
            headerName == "Height (bbox)" and value > self.maxBBoxHeight:
                return QtGui.QBrush(QtGui.QColor("#8F2B2B"))


class NodesTableView(QtGui.QTableView):
    # TODO: maybe also add the node.width/height() image size
    _headers = ["Name", "Class", "Width (bbox)", "Height (bbox)", "Disabled", "Label"]

    def __init__(self, parent = None):
        QtGui.QTableView.__init__(self, parent)

        self.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)

        self.model = NodesTableModel()
        self.model.setHeaders(self._headers)

        self.proxyModel = QtGui.QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setFilterKeyColumn(0)
        self.proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxyModel.setSourceModel(self.model)

        self.setModel(self.proxyModel)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

class NodesList():
    # TODO: self.addNode must be re-think... maybe use a dict
    # TODO: add a remove node
    # TODO: add a nuke.callback to update list on Node in DAG changed,deleted,added,...

    _ignoredNodeClass = ["BackdropNode", "Viewer", "Axis2", "Camera", "FillMat",
                         "ReadGeo2", "Scene", "Sphere", "TransformGeo", "Axis"]

    def __init__(self, data = []):
        self._nodeList = []

    @property
    def nodeList(self):
        return self._nodeList

    def addNode(self, item):
        if item:
            if item not in self._nodeList and \
            item.Class() not in self._ignoredNodeClass:
                self._nodeList.append(self.itemRow(item))

    def itemRow(self, item):
        itemRow = []

        try:
            itemRow.append(item.name())
        except:
            itemRow.append("unknown name")

        try:
            itemRow.append(item.Class())
        except:
            itemRow.append("unknown class")

        try:
            itemRow.append(item.bbox().w())
        except:
            itemRow.append(0)

        try:
            itemRow.append(item.bbox().h())
        except:
            itemRow.append(0)

        try:
            itemRow.append(item.knob("disable").value())
        except:
            itemRow.append("none")

        try:
            itemRow.append(item.knob("label").value())
        except:
            itemRow.append("")

        return itemRow

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
    for i in range(0, 60):
        node = FakeNode()
        pseudoList.addNode(node)

    app = QtGui.QApplication(sys.argv)
    app.setStyle("plastique")

    # main window
    ui = MainWindow()
    ui.tableView.model.listNodes = pseudoList.nodeList
    ui.show()

    # tableView
    #table = NodesTableView()
    #table.model.listNodes = pseudoList
    #table.resize(700, 300)

    # filter test
    #table.proxyModel.setFilterKeyColumn(1)
    #table.proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
    #table.proxyModel.setFilterWildcard("bl*")

    # test add other node after
    #otherNode = FakeNode()
    #otherNode._name = "otherNode"
    #pseudoList.addNode(otherNode)

    # test remove node from list
    #pseudoList.removeNode("otherNode")

    sys.exit(app.exec_())
