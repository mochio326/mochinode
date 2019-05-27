# # -*- coding: utf-8 -*-
from mochinode.vendor.Qt import QtCore, QtGui, QtWidgets
from . import common
from . import node
from .view import View2

class Window(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self.setWindowTitle('mochinode test app2')

        self.resize(800, 600)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(2)
        hbox.setContentsMargins(2, 2, 2, 2)
        self.setLayout(hbox)

        scene = QtWidgets.QGraphicsScene()
        scene.setObjectName('Scene')
        scene.setSceneRect(0, 0, 32000, 32000)
        self.view = View2(scene, self)

        self.central_layout = QtWidgets.QVBoxLayout()
        hbox.addWidget(self.view)
        hbox.addLayout(self.central_layout, 10)

        run_button = QtWidgets.QPushButton('Run !!!')
        run_button.clicked.connect(lambda: common.nodes_recalculation(self.view))
        run_button.setStyleSheet("background-color: rgb(244, 72, 66);")
        self.central_layout.addWidget(run_button)

        auto_layout_button = QtWidgets.QPushButton('Auto Layout')
        auto_layout_button.clicked.connect(lambda: self.view.auto_layout())
        auto_layout_button.setStyleSheet("background-color: rgb(244, 238, 65);")
        # vbox.addWidget(self.nameFld)
        # vbox.addWidget(addBtn)
        self.central_layout.addWidget(auto_layout_button)

        self.add_button('If', 'If')
        self.add_button('Less Than(<)', 'LessThan')
        self.add_button('Add(＋)', 'Add')
        self.add_button('Subtract(ー)', 'Subtract')
        self.add_button('Multiply(×)', 'Multiply')
        self.add_button('Modulo(÷)', 'Modulo')
        self.add_button('1', '1')
        self.add_button('2', '2')
        self.add_button('3', '3')
        self.add_button('4', '4')

        self.central_layout.addStretch(1)

    def add_button(self, label, xml_name):
        self.add_box_button = QtWidgets.QPushButton(label)
        self.central_layout.addWidget(self.add_box_button)
        self.add_box_button.clicked.connect(lambda: self.clickedBoxButton(xml_name))

    def clickedBoxButton(self, xml_name):
        box = node.create_node_for_xml(xml_name, self.view)
        self.view.add_node_on_center(box)
        self.view.create_history()
        # box.recalculation()


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


if __name__ == '__main__':
    main()
