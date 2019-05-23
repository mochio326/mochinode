# # -*- coding: utf-8 -*-
from mochinode.vendor.Qt import QtCore, QtGui, QtWidgets
from mochinode import Node, View, Port
from shiboken2 import wrapInstance

class Window(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self.setWindowTitle('mochinode test app')

        self.resize(800, 600)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(2)
        hbox.setContentsMargins(2, 2, 2, 2)
        self.setLayout(hbox)

        scene = QtWidgets.QGraphicsScene()
        scene.setObjectName('Scene')
        scene.setSceneRect(0, 0, 32000, 32000)
        self.view = View(scene, self)

        vbox = QtWidgets.QVBoxLayout()
        hbox.addWidget(self.view)
        hbox.addLayout(vbox, 10)
        self.nameFld = QtWidgets.QLineEdit('node')
        addBtn = QtWidgets.QPushButton('Add Node')
        addBtn.clicked.connect(self.addNode)
        layoutBtn = QtWidgets.QPushButton('Layout')
        layoutBtn.clicked.connect(lambda: self.view.auto_layout())
        vbox.addStrut(100)
        vbox.addWidget(self.nameFld)
        vbox.addWidget(addBtn)
        vbox.addWidget(layoutBtn)
        vbox.addStretch(1)

    def addNode(self):
        node = Node(label=self.nameFld.text())
        top = node.add_port(port_type='out', label='Out', color=QtCore.Qt.cyan)
        Port(top, 'Foo')
        p = Port(top, 'Bar')
        Port(p, 'BarX')
        Port(p, 'BarY')
        Port(p, 'BarZ')
        Port(top, 'Baz')
        top = node.add_port(port_type='in', label='In2', color=QtCore.Qt.green)
        p = Port(top, 'Fuga')
        Port(p, 'FugaR')
        Port(p, 'FugaG')
        Port(p, 'FugaB')
        top = node.add_port(port_type='in', label='In', color=QtCore.Qt.green)
        Port(top, 'Piyo')
        p = Port(top, 'Hoge', color=QtCore.Qt.green)
        Port(p, 'HogeX')
        Port(p, 'HogeY')
        Port(p, 'HogeZ')
        self.view.add_node_on_center(node)


'''
============================================================
---   SHOW WINDOW
============================================================
'''

def main(parent=None):
    from sys import exit, argv
    app = QtWidgets.QApplication(argv)
    nodeWindow = Window(parent)
    nodeWindow.show()
    exit(app.exec_())


def maya_main():
    import maya.OpenMayaUI as OpenMayaUI
    mainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
    mayaWindow = wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)
    nodeWindow = Window()
    nodeWindow.show()


if __name__ == '__main__':
    main()
