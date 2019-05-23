# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
import cmath

class LineArrow(QtWidgets.QGraphicsItem):
    def __init__(self, parent, color):
        super(LineArrow, self).__init__(parent)
        self.triangle = QtGui.QPolygon()
        self.color = color
        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(0)
        self.pen.setColor(self.color)

    @property
    def line(self):
        return self.parentItem()

    def paint(self, painter, option, widget):
        self.color = self.parentItem().color
        painter.setPen(self.pen)
        path = QtGui.QPainterPath()
        dx = self.line.point_b.x() - self.line.point_a.x()
        dy = self.line.point_b.y() - self.line.point_a.y()
        triangle_x = (self.line.point_a.x() + self.line.point_b.x()) / 2
        triangle_y = (self.line.point_a.y() + self.line.point_b.y()) / 2
        # パスの接線をパスの描画とは切り離して調整しないとうまいこと回転できなかった
        if dx > 0:
            ctrl1_dummy = QtCore.QPointF(self.line.point_a.x() + dx * 0.3,
                                         self.line.point_a.y() + dy * 0.1)
            ctrl2_dummy = QtCore.QPointF(self.line.point_b.x() - dx * 0.3,
                                         self.line.point_a.y() + dy * 0.9)
        else:
            ctrl1_dummy = QtCore.QPointF(self.line.point_a.x() + abs(dx * 0.7),
                                         self.line.point_a.y() + dy * 0.1)
            ctrl2_dummy = QtCore.QPointF(self.line.point_b.x() - abs(dx * 0.7),
                                         self.line.point_a.y() + dy * 0.9)

        # 三角形の中心からの先端へのベクトル
        line_vector_x = ctrl1_dummy.x() - ctrl2_dummy.x()
        line_vector_y = ctrl1_dummy.y() - ctrl2_dummy.y()
        line_vector = complex(line_vector_x, line_vector_y)
        # 単位ベクトルに変換
        _p = cmath.phase(line_vector)
        line_vector = cmath.rect(1, _p)

        #
        triangle_points = [complex(-5, 0),
                           complex(5, 7),
                           complex(5, -7),
                           complex(-5, 0)]
        triangle_points = [_p * line_vector for _p in triangle_points]
        triangle_points = [QtCore.QPoint(triangle_x + _p.real, triangle_y + _p.imag) for _p in triangle_points]
        self.triangle = QtGui.QPolygon(triangle_points)
        path.addPolygon(self.triangle)
        painter.fillPath(path, self.pen.color())
        painter.drawPath(path)

    def boundingRect(self):
        return self.triangle.boundingRect()

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path


class Line(QtWidgets.QGraphicsPathItem):
    DEF_Z_VALUE = 0.0

    @classmethod
    def scene_lines_iter(cls, scene):
        # シーン内のノードのみ取得
        for _i in scene.items():
            if type(_i) != cls:
                continue
            yield _i

    @property
    def _tooltip(self):
        if self.source is None or self.target is None:
            return ''
        return '{}.{} -> {}.{}'.format(self.source.node.name, self.source.name, self.target.node.name, self.target.name)

    def __init__(self, point_a, point_b, color):
        super(Line, self).__init__()
        self.color = color
        self._point_a = point_a
        self._point_b = point_b
        self._source = None
        self._target = None
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(self.color)
        self.hover_port = None
        self.arrow = LineArrow(self, self.color)

        self.setZValue(self.DEF_Z_VALUE)
        self.setBrush(QtCore.Qt.NoBrush)
        self.setPen(self.pen)
        self.setAcceptHoverEvents(True)
        self.port_connected = False

    def _get_none_move_port(self):
        if self.source is None:
            return self.target
        return self.source

    def _can_edit(self):
        #  どちらかのポートが非表示なとき編集できると混乱するので不可
        if self.source is not None:
            if not self.source.isVisible():
                return False
        if self.target is not None:
            if not self.target.isVisible():
                return False
        return True

    def update_moving_point(self, pos):
        if self.source is None:
            self.point_a = pos
        else:
            self.point_b = pos

    def delete(self):
        if self.source is not None:
            port = self.source
            self.source.change_to_basic_color()
            self.source.disconnect_line(self)
        if self.target is not None:
            port = self.target
            self.target.change_to_basic_color()
            self.target.disconnect_line(self)

        self.scene().views()[0].remove_item(self)

        # 既に接続済みだった場合のみsignal発火
        if self.port_connected:
            port.node.port_connect_changed.emit()
            port.node.port_disconnect.emit()

    def mousePressEvent(self, event):
        #  どちらかのポートが非表示なとき編集できると混乱するので不可
        if not self.source.isVisible() or not self.target.isVisible():
            return

        pos = event.scenePos().toPoint()
        pos_to_a = self.point_a - pos
        pos_to_b = self.point_b - pos
        # ベクトルの長さ
        vector_a_abs = abs(complex(pos_to_a.x(), pos_to_a.y()))
        vector_b_abs = abs(complex(pos_to_b.x(), pos_to_b.y()))

        # どちら側に近いかで切り離すポートを区別
        if vector_a_abs < vector_b_abs:
            self.point_a = event.pos()
            self.source.disconnect_line(self)
        else:
            self.point_b = event.pos()
            self.target.disconnect_line(self)

    def mouseMoveEvent(self, event):
        if not self._can_edit():
            return

        # 一度ラインを後ろにもっていかないとライン自体をitemとして取得してしまう
        self.setZValue(self.DEF_Z_VALUE)

        pos = event.scenePos().toPoint()
        self.update_moving_point(pos)
        none_move_port = self._get_none_move_port()

        # ポートのハイライト
        pos = event.scenePos().toPoint()
        item = self.scene().itemAt(pos.x(), pos.y(), QtGui.QTransform())

        if isinstance(item, none_move_port.__class__):
            if none_move_port.can_connection(item):
                self.hover_port = item
                self.hover_port.change_to_hover_color()
                self.update_moving_point(item.get_center())
        else:
            if self.hover_port is not None:
                self.hover_port.change_to_basic_color()
                self.hover_port = None

        self.setZValue(100)
        self.scene().update()

    def mouseReleaseEvent(self, event):
        if not self._can_edit():
            return

        self.setZValue(self.DEF_Z_VALUE)
        pos = event.scenePos().toPoint()
        item = self.scene().itemAt(pos.x(), pos.y(), QtGui.QTransform())

        # ポート以外で離したらラインごと削除
        none_move_port = self._get_none_move_port()
        if not isinstance(item, none_move_port.__class__):
            self.delete()
            return False

        _none_move_port = self._get_none_move_port()

        if not _none_move_port.can_connection(item):
            self.delete()
            return False

        item.connect_line(self)
        _none_move_port.connect_line(self)

        item.node.port_connect_changed.emit()
        item.node.port_connect.emit()
        self.port_connected = True
        return True

    def update_path(self):
        if self.source is not None and self.target is not None:
            if not self.target.isVisible() and not self.source.isVisible():
                self.setVisible(False)
                return
            else:
                self.setVisible(True)
                self._point_a = self.source.get_center()
                self._point_b = self.target.get_center()

        path = QtGui.QPainterPath()
        path.moveTo(self.point_a)
        dx = self.point_b.x() - self.point_a.x()
        dy = self.point_b.y() - self.point_a.y()
        ctrl1 = QtCore.QPointF(self.point_a.x() + abs(dx * 0.7), self.point_a.y() + dy * 0.1)
        ctrl2 = QtCore.QPointF(self.point_b.x() - abs(dx * 0.7), self.point_a.y() + dy * 0.9)
        path.cubicTo(ctrl1, ctrl2, self.point_b)
        self.setPath(path)

    def hoverMoveEvent(self, event):
        pass

    def hoverEnterEvent(self, event):
        self.setToolTip(self._tooltip)
        self.pen.setColor(QtGui.QColor(255, 200, 200, 255))
        self.arrow.pen.setColor(QtGui.QColor(255, 200, 200, 255))
        self.setPen(self.pen)
        self.target.change_to_hover_color()
        self.source.change_to_hover_color()

    def hoverLeaveEvent(self, event):
        self.pen.setColor(self.color)
        self.arrow.pen.setColor(self.color)
        self.setPen(self.pen)
        self.target.change_to_basic_color()
        self.source.change_to_basic_color()

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.drawPath(self.path())
        self.arrow.paint(painter, option, widget)

    @property
    def point_a(self):
        return self._point_a

    @point_a.setter
    def point_a(self, point):
        self._point_a = point
        self.update_path()

    @property
    def point_b(self):
        return self._point_b

    @point_b.setter
    def point_b(self, point):
        self._point_b = point
        self.update_path()

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, widget):
        self._source = widget
        self._source = widget

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, widget):
        self._target = widget


class TempLine(Line):
    def __init__(self, point_a, point_b):
        super(TempLine, self).__init__(point_a, point_b, QtGui.QColor(244, 127, 65))
        self.pen.setStyle(QtCore.Qt.DotLine)

    def delete(self):
        if self.source is not None:
            self.source.disconnect_temp_line(self)
        if self.target is not None:
            self.target.disconnect_temp_line(self)
        self.scene().views()[0].remove_item(self)

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass
# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
