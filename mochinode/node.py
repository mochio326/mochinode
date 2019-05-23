# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import port
import uuid

class NodeLabel(QtWidgets.QGraphicsItem):

    @property
    def node(self):
        return self.parentItem()

    def __init__(self, parent, label):
        super(NodeLabel, self).__init__(parent)
        self.rect = QtCore.QRect(0, 0, self.node.width, 20)
        self.label = label
        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QtGui.QColor(200, 200, 200, 255))

        self.brush = QtGui.QLinearGradient(0, 0, self.node.width, 0)
        self.brush.setColorAt(0.0, QtGui.QColor(68, 160, 122))
        self.brush.setColorAt(1.0, QtGui.QColor(60, 60, 60, 255))

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawPath(self.shape())

        painter.setPen(self.pen)
        painter.setFont(QtGui.QFont('Decorative', 10))
        rect = self.boundingRect()
        rect.moveTop(rect.y() - 2)
        painter.drawText(rect, QtCore.Qt.AlignCenter, self.label)

    def boundingRect(self):
        rect = QtCore.QRect(0, 0, self.node.width, 20)
        return QtCore.QRectF(rect)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(1, 1, self.node.width - 2, 19), 9, 9)
        path2 = QtGui.QPainterPath()
        path2.addPolygon(QtCore.QRectF(1, 10, self.node.width - 2, 10))
        path3 = path.united(path2)
        return path3


class Node(QtWidgets.QGraphicsObject):
    DEF_Z_VALUE = 0.1

    moved = QtCore.Signal()
    port_expanded = QtCore.Signal()
    port_connect_changed = QtCore.Signal()
    port_connect = QtCore.Signal()
    port_disconnect = QtCore.Signal()


    @classmethod
    def scene_nodes_iter(cls, scene):
        # シーン内のノードのみ取得
        for _i in scene.items():
            if not isinstance(_i, cls):
                continue
            yield _i

    @property
    def rect(self):
        return QtCore.QRect(0, 0, self.width, self.height)

    @property
    def ports(self):
        # リストでアクセス用
        return [_item for _item in self.childItems() if isinstance(_item, port.Port)]

    @property
    def port(self):
        # 辞書でアクセス用
        return {str(_p.name):_p for _p in self.children_ports_all_iter()}

    def __init__(self, name='', width=140, height=60, label='node'):
        super(Node, self).__init__()
        self.id = str(uuid.uuid4())
        self.name = name
        self.setZValue(self.DEF_Z_VALUE)
        self.width = width
        self.height = height
        self.drag = False

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

        # Brush.
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(QtGui.QColor(60, 60, 60, 255))

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QtGui.QColor(140, 140, 140, 255))

        self.sel_pen = QtGui.QPen()
        self.sel_pen.setStyle(QtCore.Qt.SolidLine)
        self.sel_pen.setWidth(2)
        self.sel_pen.setColor(QtGui.QColor(0, 255, 255, 255))

        self.forced_recalculation = False
        self.recalculation_weight = 0


        if label is not None:
            self.label = NodeLabel(self, label)
            self.port_init_y = 30
        else:
            self.port_init_y = 10

        self.moved.connect(self.update_connect_all_line_pos)


    def refresh_id(self):
        self.id = str(uuid.uuid4())

    def add_port(self, port_type, color, value_type=None, label=None, value=None):
        p = port.Port(self, port_type=port_type, color=color, value_type=value_type, label=label, value=value)
        self.deploying_port()
        self.update()
        return p

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        if self.isSelected():
            painter.setPen(self.sel_pen)
        else:
            painter.setPen(self.pen)
        painter.drawRoundedRect(self.rect, 10.0, 10.0)

    def deploying_port(self):
        _port_y = self.port_init_y
        for _p in self.ports:
            _p.setY(_port_y)
            _port_y = _port_y + _p.height_space
            _p.update_connect_line_pos()
            _p.deploying_port()
        self.height = _port_y + 5

    def get_source_nodes(self):
        return self.get_connection_node('out', 'source')

    def get_target_nodes(self):
        return self.get_connection_node('in', 'target')

    def get_connection_node(self, port_type, line_side):
        nodes = []
        for _p in self.children_ports_all_iter():
            if _p.type == port_type:
                continue
            for _l in _p.lines:
                n = getattr(_l, line_side).node
                nodes.append(n)
                nodes.extend(n.get_connection_node(port_type, line_side))
        return list(set(nodes))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton and event.modifiers() == QtCore.Qt.ControlModifier:

            self.scene().clearSelection()
            for _n in self.get_source_nodes():
                _n.setSelected(True)
            self.setSelected(True)
            self.scene().update()

        elif event.button() == QtCore.Qt.LeftButton:
            self.drag = True
            # 自身と関連するラインを見やすくするために最前面表示
            self.setZValue(100.0)
            for _p in self.children_ports_all_iter():
                for _l in _p.lines:
                    _l.setZValue(100.0)
        super(Node, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(Node, self).mouseMoveEvent(event)

        if self.drag:
            # 自身以外も選択されている場合にまとめて処理する
            # for _n in self.scene().selectedItems():
            #     for _p in _n.children_ports_all_iter():
            #         _p.update_connect_line_pos()
            self.moved.emit()
            self.scene().update()

    def update_connect_all_line_pos(self):
        for _n in self.scene().selectedItems():
            for _p in _n.children_ports_all_iter():
                _p.update_connect_line_pos()

    def mouseReleaseEvent(self, event):
        if self.drag:
            self.drag = False

            # ノードを現在の描画順を維持したまま数値を整頓
            node_z_list = []
            for _n in self.scene_nodes_iter(self.scene()):
                node_z_list.append([_n.zValue(), _n])
            node_z_list = sorted(node_z_list, key=lambda x:x[0])
            for _i, _n in enumerate(node_z_list):
                _n[1].setZValue(self.DEF_Z_VALUE + 0.01 * _i)
            # ラインは最後面に戻しとく
            for _p in self.children_ports_all_iter():
                for _l in _p.lines:
                    _l.setZValue(_l.DEF_Z_VALUE)
            super(Node, self).mouseReleaseEvent(event)
            self.moved.emit()

    def delete(self):
        for _p in self.children_ports_all_iter():
            _p.delete_all_line()
        self.scene().views()[0].remove_item(self)

    def children_ports_all_iter(self):
        for _p in self.ports:
            yield _p
            for _pp in _p.children_ports_all_iter():
                yield _pp

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
