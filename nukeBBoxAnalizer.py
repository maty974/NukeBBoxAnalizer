'''
Created on Mar 25, 2012

@author: Matthieu Cadet
@contact: matthieu.cadet@gmail.com
'''

# FIXME: MainWindow call with parent=None cause nuke crash on exit
# when the window is still opened

import operator
from PySide import QtCore, QtGui
try:
    import nuke
    import nukescripts
except:
    pass

__author__ = "Matthieu Cadet"
__maintainer__ = "Matthieu Cadet"
__email__ = "matthieu.cadet@gmail.com"
__copyright__ = "Copyright 2012"
__license__ = "?"
__version__ = "1.0"

def centerNodeInNodeGraph(node):
    try:
        xpos = node["xpos"].value()
        ypos = node["ypos"].value()
        factor = 1.0
        nukescripts.clear_selection_recursive()
        node["selected"].setValue(True)
        nuke.zoom(factor, (xpos, ypos))
    except:
        pass

class FilterWidget(QtGui.QHBoxLayout):
    def __init__(self, parent = None):
        QtGui.QHBoxLayout.__init__(self, parent)

        self.entry = QtGui.QLineEdit()
        self.type = QtGui.QComboBox()
        self.type.addItems(NodesTableView._headers)

        self.addWidget(self.type)
        self.addWidget(self.entry)

class TargetFormatWidget(QtGui.QHBoxLayout):
    _testData = ["640x480 PC_Video",
            "720x486 NTSC",
            "720x576 PAL",
            "1920x1080 HD",
            "720x486 NTSC_16:9",
            "720x576 PAL_16:9" ]

    def __init__(self, parent = None):
        QtGui.QHBoxLayout.__init__(self, parent)

        self.list = self.initFormatList()

        self.format = QtGui.QComboBox()
        self.format.addItems(self.list)
        self.format.setCurrentIndex(self.currentNukeFormatIndex)

        self.addWidget(self.format)

    def initFormatList(self):
        try:
            listFormat = []
            for nFormat in nuke.formats():
                item = "%sx%s %s " % (nFormat.width(), nFormat.height(), nFormat.name())
                listFormat.append(item)

            return listFormat
        except:
            return self._testData

    def getResolutionFromIndex(self, index):
        width, height = self.list[index].split()[0].split("x")
        return width, height

    @property
    def currentNukeFormatIndex(self):
        """
        Get current format in Nuke
        """

        try:
            nFormat = nuke.Root().format()
            currentFormat = "%sx%s %s " % (nFormat.width(), nFormat.height(), nFormat.name())
            return self.list.index(currentFormat)
        except:
            return 0

class InfosCountStatus(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self._totalNodes = 0
        self._oversizeBBox = 0

        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(2, 2, 2, 2)

        labelFrameStyle = QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken

        self.labelTotalNodes = QtGui.QLabel("total nodes: %s" % self._totalNodes)
        self.labelTotalNodes.setFrameStyle(labelFrameStyle)

        self.labelOversizeBBox = QtGui.QLabel("oversize bbox: %s" % self._oversizeBBox)
        self.labelOversizeBBox.setFrameStyle(labelFrameStyle)

        hbox.addWidget(self.labelTotalNodes)
        hbox.addWidget(self.labelOversizeBBox)

        hbox.setSizeConstraint(QtGui.QHBoxLayout.SetFixedSize)

        self.setLayout(hbox)

    @property
    def totalNodes(self):
        return self._totalNodes
    @totalNodes.setter
    def totalNodes(self, value):
        self._totalNodes = value
        self.labelTotalNodes.setText("total nodes: %s" % self.totalNodes)

    @property
    def oversizeBBox(self):
        return self._oversizeBBox

    @oversizeBBox.setter
    def oversizeBBox(self, value):
        self._oversizeBBox = value
        self.labelOversizeBBox.setText("oversize bbox: %s" % self.oversizeBBox)


class MainWindow(QtGui.QDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle("Nuke BBox Analizer | %s" % __version__)
        self.setObjectName("NukeBBoxAnalizerWindow")
        self.resize(800, 600)

        self.filterGroup = QtGui.QGroupBox("Filter")
        self.filterWidget = FilterWidget()
        self.filterGroup.setLayout(self.filterWidget)

        self.targetFormatGroup = QtGui.QGroupBox("Target Format")
        self.targetFormatWidget = TargetFormatWidget()
        self.targetFormatGroup.setLayout(self.targetFormatWidget)

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

        self.nodeLister = NodesList()
        self.nodeLister.setFromNukeNodes()
        self.tableView.model.listNodes = self.nodeLister.nodeList

        self.hboxStatusBar.addWidget(self.infosCountStatus)
        self.hboxStatusBar.addWidget(self.refreshButton)

        self.vboxLayout.addLayout(self.hboxTopLayout)
        self.hboxTopLayout.addWidget(self.filterGroup)
        self.hboxTopLayout.addWidget(self.targetFormatGroup)
        self.vboxLayout.addWidget(self.tableView)
        self.vboxLayout.addLayout(self.hboxBottomLayout)
        self.hboxBottomLayout.addWidget(self.nodeActionsGroup)
        self.hboxBottomLayout.addWidget(self.displayOptionsGroup)
        self.vboxLayout.addLayout(self.hboxStatusBar)

        self.setLayout(self.vboxLayout)

        # connect some widgets signal
        self.filterWidget.entry.textChanged.connect(self.setFilter)
        self.filterWidget.entry.textChanged.connect(self.setInfosCount)
        self.filterWidget.type.currentIndexChanged.connect(self.setFilterColumn)
        self.tableView.proxyModel.layoutChanged.connect(self.setInfosCount)
        self.refreshButton.clicked.connect(self.refreshListOfNodes)
        self.targetFormatWidget.format.currentIndexChanged.connect(self.setFormat)

        # emit table model layoutChanged
        self.tableView.model.layoutChanged.emit()
        self.setFormat()

    def refreshListOfNodes(self):
        self.nodeLister.setFromNukeNodes()
        self.tableView.model.listNodes = self.nodeLister.nodeList

    def addNukeCallBacks(self):
        try:
            nuke.addOnUserCreate(self.refreshListOfNodes)
            nuke.addOnDestroy(self.refreshListOfNodes)
        except:
            pass

    def removeNukeCallBacks(self):
        try:
            nuke.removeOnUserCreate(self.refreshListOfNodes)
            nuke.removeOnDestroy(self.refreshListOfNodes)
        except:
            pass

    def setInfosCount(self):
        self.infosCountStatus.totalNodes = self.tableView.proxyModel.rowCount()

    def setFilterColumn(self, name):
        self.tableView.proxyModel.setFilterKeyColumn(self.tableView._headers.index(name))

    def setFilter(self, pattern):
        self.tableView.proxyModel.setFilterRegExp(pattern)

    def setFormat(self):
        width, height = self.targetFormatWidget.getResolutionFromIndex(self.targetFormatWidget.format.currentIndex())
        self.tableView.model.maxBBoxWidth = width
        self.tableView.model.maxBBoxHeight = height

    def event(self, event):
        return QtGui.QWidget.event(self, event)

    def closeEvent(self, event):
        self.removeNukeCallBacks()
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
        self._maxBBoxWidth = int(value)
        self.layoutChanged.emit()

    @property
    def maxBBoxHeight(self):
        return self._maxBBoxHeight

    @maxBBoxHeight.setter
    def maxBBoxHeight(self, value):
        self._maxBBoxHeight = int(value)
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
        value = self._listNodes[row][column]

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
        self.doubleClicked.connect(self.focusNukeNode)

    def focusNukeNode(self, data):
        try:
            nodename = data.child(data.row(), 0).data()
            node = nuke.toNode(nodename)

            centerNodeInNodeGraph(node)
        except:
            pass

class NodesList(object):
    # TODO: self.addNode must be re-think... maybe use a dict
    # TODO: add a remove node
    # TODO: add a nuke.callback to update list on Node in DAG changed,deleted,added,...

    _ignoredNodeClass = ["BackdropNode", "Viewer", "Axis2", "Camera", "FillMat",
                         "ReadGeo2", "Scene", "Sphere", "TransformGeo", "Axis"]

    def __init__(self):
        self._nodeList = []

    @property
    def nodeList(self):
        return self._nodeList

    def addNode(self, item):
        if item:
            if item not in self._nodeList and \
            item.Class() not in self._ignoredNodeClass:
                self._nodeList.append(self.itemRow(item))

    def setFromNukeNodes(self):
        try:
            self.clearList()
            for node in nuke.allNodes():
                self.addNode(node)
        except:
            pass

    def clearList(self):
        self._nodeList = []

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

def startBBoxAnalizer():
    global uiBBoxAnalizer

    # main window
    uiBBoxAnalizer = MainWindow()
    uiBBoxAnalizer.show()

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
    for i in range(0, 10):
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
