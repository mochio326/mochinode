# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import line


class PortExpandBox(QtWidgets.QGraphicsItem):
    BOX_SIZE = 10

    @property
    def port(self):
        return self.parentItem()

    def __init__(self, parent):
        super(PortExpandBox, self).__init__(parent)
        self.height = self.BOX_SIZE

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QtGui.QColor(125, 125, 125, 255))

    def paint(self, painter, option, widget):
        if len(self.port.children_port) == 0:
            self.setVisible(False)
            return
        self.setVisible(True)
        painter.setPen(self.pen)
        painter.drawPath(self.shape())

    def boundingRect(self):
        rect = QtCore.QRect(0, 0, 10, self.height)
        return QtCore.QRectF(rect)

    def shape(self):
        offset_parent = self.port.parent_port_count() * 20

        if self.port.type == 'in':
            base_x = (self.port.PORT_SIZE / 2) + offset_parent + 3
        else:
            base_x = self.port.node.width - self.port.PORT_SIZE - offset_parent - 8

        box = QtGui.QPainterPath()
        box.addPolygon(QtCore.QRectF(base_x, 0, self.BOX_SIZE, self.BOX_SIZE))

        box_horizontal = QtGui.QPainterPath()
        box_horizontal.moveTo(base_x, self.BOX_SIZE / 2)
        box_horizontal.lineTo(self.BOX_SIZE + base_x, self.BOX_SIZE / 2)

        box.addPath(box_horizontal)

        if self.port.type == 'in':
            children_line_x = round(self.BOX_SIZE * 1.5)
        else:
            children_line_x = round(self.BOX_SIZE / 0.75) * -1
        children_line_x = children_line_x + base_x

        if not self.port.children_port_expand:
            box_vertical = QtGui.QPainterPath()
            box_vertical.moveTo(self.BOX_SIZE / 2 + base_x, 0)
            box_vertical.lineTo(self.BOX_SIZE / 2 + base_x, self.BOX_SIZE)
            box.addPath(box_vertical)
        else:
            # Children's line
            y_min = self.BOX_SIZE
            for _p in self.port.children_port:
                y_max = _p.y() + self.BOX_SIZE / 2

                vertical_line = QtGui.QPainterPath()
                vertical_line.moveTo(self.BOX_SIZE / 2 + base_x, y_min)
                vertical_line.lineTo(self.BOX_SIZE / 2 + base_x, y_max)
                box.addPath(vertical_line)

                horizontal_line = QtGui.QPainterPath()
                horizontal_line.moveTo(children_line_x, y_max)
                horizontal_line.lineTo(self.BOX_SIZE / 2 + base_x, y_max)
                box.addPath(horizontal_line)

            self.height = y_max

        return box

    def mousePressEvent(self, event):
        self.port.expand()


class PortLabel(QtWidgets.QGraphicsItem):

    @property
    def font(self):
        return QtGui.QFont('Decorative', self.text_size)

    @property
    def port(self):
        return self.parentItem()

    def __init__(self, parent, label):
        super(PortLabel, self).__init__(parent)
        self.label = label
        self.text_size = 10
        self.port_value_visible = True

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(2)
        self.pen.setColor(QtGui.QColor(200, 200, 200, 255))

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setFont(self.font)
        _labal = self._get_label()
        painter.drawText(self.boundingRect(), self.text_align, _labal)

    def _get_label(self):
        l = self.label
        if self.port_value_visible:
            l = l + '[' + str(self.port.value) + ']'
        return l

    def boundingRect(self):
        font_metrics = QtGui.QFontMetrics(self.font)
        _labal = self._get_label()
        width = font_metrics.width(_labal)
        height = font_metrics.height()
        # ベースラインから下降サイズを無視する
        # こういう場合、height()ではなく、ascent()を使ってもOK!
        # height = height - font_metrics.descent()

        offset_parent = self.port.parent_port_count() * 20
        if len(self.port.children_port) > 0:
            offset_child = 10
        else:
            offset_child = 0

        if self.port.type == 'in':
            self.text_align = QtCore.Qt.AlignLeft
            label_x = self.port.PORT_SIZE + 2 + offset_parent + offset_child
        else:
            self.text_align = QtCore.Qt.AlignRight
            label_x = self.port.node.width - width - self.port.PORT_SIZE - offset_parent - offset_child

        return QtCore.QRect(label_x, 0 - self.text_size / 2, width, height)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def mousePressEvent(self, event):
        self.port.expand()


class Port(QtWidgets.QGraphicsObject):
    PORT_SIZE = 12
    INTERVAL_SIZE = 25

    @property
    def node(self):
        return self.topLevelItem()

    @property
    def children_port(self):
        return [_item for _item in self.childItems() if isinstance(_item, Port)]

    @property
    def height_space(self):
        if not self.children_port_expand:
            return self.INTERVAL_SIZE
        h = self.INTERVAL_SIZE
        for _p in self.children_port:
            h = h + _p.height_space
        return h

    def __init__(self, parent, label, port_type=None, color=None, value_type=None, value=None):
        super(Port, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self.color = color
        self.value_type = value_type
        self.hover_port = None
        self.type = port_type
        self.new_line = None
        self.children_port_expand = False
        self.name = label
        self.value = value

        if isinstance(parent, Port):
            rect_x = parent.rect.x()
            self.type = parent.type
            if color is None:
                self.color = parent.color
        else:
            if self.type == 'in':
                rect_x = 0 - self.PORT_SIZE / 2
            else:
                rect_x = parent.width - self.PORT_SIZE / 2

        self.rect = QtCore.QRect(rect_x, 0, 12, 12)

        if label is not None:
            self.label = PortLabel(self, label)

        self.expand_box = PortExpandBox(self)

        # Brush.
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(QtCore.Qt.red)

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(2)
        self.pen.setColor(self.color)

        # line.Lines.
        self.lines = []
        self.temp_lines = []

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def boundingRect(self):
        return QtCore.QRectF(self.rect.x() - 5.0, self.rect.y() - 5.0, self.rect.width() + 5.0,
                             self.rect.height() + 5.0)

    def paint(self, painter, option, widget):

        if len(self.lines) == 0:
            self.brush.setColor(QtGui.QColor(60, 60, 60, 255))
        else:
            for _l in self.lines:
                if isinstance(_l, line.Line):
                    self.brush.setColor(self.color)
                    break
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawEllipse(self.rect)

    def hoverMoveEvent(self, event):
        if self.isUnderMouse():
            self.change_to_hover_color()
            self.node.update()

    def hoverEnterEvent(self, event):
        pass

    def hoverLeaveEvent(self, event):
        self.change_to_basic_color()
        self.node.update()

    def mousePressEvent(self, event):
        self.hover_port = None

        if self.type == 'out':
            point_a = self.get_center()
            point_b = self.mapToScene(event.pos())

        elif self.type == 'in':
            point_a = self.mapToScene(event.pos())
            point_b = self.get_center()

        self.new_line = line.Line(point_a, point_b, self.color)
        self.scene().views()[0].add_item(self.new_line)
        self.connect_line(self.new_line, True)

    def mouseMoveEvent(self, event):
        self.new_line.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        _f = self.new_line.mouseReleaseEvent(event)

    def parent_port_count(self):
        count = int(0)
        for _ in self._parent_port_iter():
            count = count + 1
        return count

    def check_parent_port_open(self):
        _flag = []
        for _p in self._parent_port_iter():
            _flag.append(_p.children_port_expand)
        return all(_flag)

    def _parent_port_iter(self):
        _p = self.parentItem()
        while isinstance(_p, Port):
            yield _p
            _p = _p.parentItem()

    def children_ports_all_iter(self):
        for _p in self.children_port:
            yield _p
            for _pp in _p.children_ports_all_iter():
                yield _pp

    def get_visible_parent_port(self):
        for _p in self._parent_port_iter():
            if _p.isVisible():
                return _p

    def expand(self):
        if len(self.children_port) == 0:
            return
        self.children_port_expand = not self.children_port_expand
        self.delete_temp_line()
        self.node.deploying_port()
        self.create_temp_line()
        self.node.update()
        self.scene().update()
        self.node.port_expanded.emit()

    def delete_temp_line(self):
        if not self.children_port_expand:
            return
        # スライスで反転してから消さないとリストが途中で狂うので注意
        for _l in self.temp_lines[::-1]:
            _l.delete()

    def delete_all_line(self):
        for _l in self.temp_lines[::-1]:
            _l.delete()
        for _l in self.lines[::-1]:
            _l.delete()

    def create_temp_line(self):
        hide_lines = self.check_children_lines_hide()
        for _l in hide_lines:
            _source = _l.source.get_visible_parent_port()
            _target = _l.target.get_visible_parent_port()
            point_a = _source.get_center()
            point_b = _target.get_center()
            _temp_line = line.TempLine(point_a, point_b)
            self.scene().views()[0].add_item(_temp_line)
            _source.connect_temp_line(_temp_line)
            _target.connect_temp_line(_temp_line)

    def check_children_lines_hide(self):
        vis_list = []
        for _p in self.children_port:
            for _l in _p.lines:
                if not _l.isVisible():
                    vis_list.append(_l)
            vis_list.extend(_p.check_children_lines_hide())
        return vis_list

    def deploying_port(self):
        if self.children_port_expand and self.check_parent_port_open():
            _port_y = self.INTERVAL_SIZE
        else:
            _port_y = 0
        for _p in self.children_port:
            _p.setVisible(self.children_port_expand)
            _p.setY(_port_y)
            if self.children_port_expand and self.check_parent_port_open():
                _port_y = _port_y + _p.height_space
            _p.update_connect_line_pos()
            _p.deploying_port()

    def change_to_hover_color(self):
        self.pen.setColor(QtGui.QColor(255, 200, 200, 255))
        self.brush.setColor(QtGui.QColor(180, 120, 190, 255))
        self.update()

    def change_to_basic_color(self):
        self.pen.setColor(self.color)
        self.brush.setColor(QtGui.QColor(180, 20, 90, 255))
        self.update()

    def disconnect_line(self, line_):
        if line_ not in self.lines:
            return
        if self.type == 'in':
            line_.target = None
        else:
            line_.source = None
        self.lines.remove(line_)
        self.change_to_basic_color()
        self.update()

    def disconnect_temp_line(self, line_):
        if line_ not in self.temp_lines:
            return
        if self.type == 'in':
            line_.target = None
        else:
            line_.source = None
        self.temp_lines.remove(line_)
        self.update()

    def connect_line(self, line_, not_del=False):
        if self.type == 'in':
            if len(self.lines) > 0 and not not_del:
                _l = self.lines[0]
                # 別のラインが接続済みだったら削除しておく
                if line_ != _l:
                    _l.delete()
                self.lines = []
            line_.target = self
        else:
            line_.source = self
        if not not_del:
            self.lines.append(line_)
        self.lines = list(set(self.lines))
        line_.update_path()
        self.update()

    def connect_temp_line(self, line_):
        if self.type == 'in':
            line_.target = self
            line_.point_b = self.get_center()
        else:
            line_.source = self
            line_.point_a = self.get_center()
        self.temp_lines.append(line_)
        self.update()

    def get_center(self):
        center = QtCore.QPointF(self.rect.x() + self.rect.width() / 2, self.rect.y() + self.rect.height() / 2)
        return self.mapToScene(center)

    def can_connection(self, port):
        if self.type == port.type:
            return False
        if self.node == port.node:
            return False
        if self.value_type != port.value_type:
            return False
        return True

    def update_connect_line_pos(self):
        for _l in self.lines:
            _l.update_path()
        for _l in self.temp_lines:
            _l.update_path()
        for cp in self.children_port:
            cp.update_connect_line_pos()

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
