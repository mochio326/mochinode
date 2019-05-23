# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import node
from . import line
import os
import subprocess
import re


class View(QtWidgets.QGraphicsView):
    """
    QGraphicsView for displaying the nodes.

    :param scene: QGraphicsScene.
    :param parent: QWidget.
    """

    def __init__(self, scene, parent):
        super(View, self).__init__(parent)
        self.setObjectName('View')
        self.setScene(scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)
        self.drag = False
        self.add_items = []
        self._operation_history = [None]
        self._current_operation_history = 0
        self.setStyleSheet('background-color: rgb(40,40,40);')

    def drawBackground(self, painter, rect):
        scene_height = self.sceneRect().height()
        scene_width = self.sceneRect().width()

        # Pen.
        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(QtGui.QColor(80, 80, 80, 125))

        sel_pen = QtGui.QPen()
        sel_pen.setStyle(QtCore.Qt.SolidLine)
        sel_pen.setWidth(1)
        sel_pen.setColor(QtGui.QColor(125, 125, 125, 125))

        grid_width = 20
        grid_height = 20
        grid_horizontal_count = int(round(scene_width / grid_width)) + 1
        grid_vertical_count = int(round(scene_height / grid_height)) + 1

        for x in range(0, grid_horizontal_count):
            xc = x * grid_width
            if x % 5 == 0:
                painter.setPen(sel_pen)
            else:
                painter.setPen(pen)
            painter.drawLine(xc, 0, xc, scene_height)

        for y in range(0, grid_vertical_count):
            yc = y * grid_height
            if y % 5 == 0:
                painter.setPen(sel_pen)
            else:
                painter.setPen(pen)
            painter.drawLine(0, yc, scene_width, yc)

    def wheelEvent(self, event):
        """
        Zooms the QGraphicsView in/out.

        :param event: QGraphicsSceneWheelEvent.
        """
        in_factor = 1.25
        out_factor = 1 / in_factor
        old_pos = self.mapToScene(event.pos())
        if event.delta() > 0:
            zoom_factor = in_factor
        else:
            zoom_factor = out_factor
        self.scale(zoom_factor, zoom_factor)
        new_pos = self.mapToScene(event.pos())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton and event.modifiers() == QtCore.Qt.AltModifier:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.drag = True
            self.prev_pos = event.pos()
            self.setCursor(QtCore.Qt.SizeAllCursor)
        elif event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        super(View, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag:
            # 等倍scaleかつ回転してないはずでscale取り出す…
            new_scale = self.matrix().m11()
            delta = (self.mapToScene(event.pos()) - self.mapToScene(self.prev_pos)) * -1.0 * new_scale
            center = QtCore.QPoint(self.viewport().width() / 2 + delta.x(), self.viewport().height() / 2 + delta.y())
            new_center = self.mapToScene(center)
            self.centerOn(new_center)
            self.prev_pos = event.pos()
            return
        super(View, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drag:
            self.drag = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        super(View, self).mouseReleaseEvent(event)
        return False

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            event.ignore()
            return

        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            # この辺りの処理は各関数をオーバーライドアプリ側での独自実装
            if event.key() == QtCore.Qt.Key_C:
                self._copy()
                return
            if event.key() == QtCore.Qt.Key_V:
                self._paste()
                return
            if event.key() == QtCore.Qt.Key_X:
                self._cut()
                return
            if event.key() == QtCore.Qt.Key_Z:
                self._undo()
                return
            if event.key() == QtCore.Qt.Key_Y:
                self._redo()
                return

        if event.key() == QtCore.Qt.Key_F:
            self.selected_item_focus()
            return

        if event.key() == QtCore.Qt.Key_A:
            self.all_item_focus()
            return

        if event.key() == QtCore.Qt.Key_Delete:
            self._delete()
            return

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            event.ignore()
            return

    def selected_item_focus(self):
        self.focus(self.scene().selectedItems())

    def all_item_focus(self):
        self.focus(self.add_items)

    def focus(self, items):
        if len(items) == 0:
            return
        self.resetMatrix()
        rect = QtCore.QRectF(0, 0, 0, 0)
        for _i in items:
            rect = rect.united(_i.sceneBoundingRect())
        center = QtCore.QPoint(rect.width() / 2 + rect.x(), rect.height() / 2 + rect.y())
        w_s = self.width() / rect.width()
        h_s = self.height() / rect.height()
        zoom_factor = w_s if w_s < h_s else h_s
        zoom_factor = zoom_factor * 0.9
        self.scale(zoom_factor, zoom_factor)
        self.centerOn(center)

    def add_node_on_center(self, node):
        self.add_item(node)
        _pos = self.mapToScene(self.width() / 2, self.height() / 2)
        node.setPos(_pos)
        node.deploying_port()
        node.update()

    def add_item(self, widget):
        if not isinstance(widget, list):
            widget = [widget]
        for _w in widget:
            self.add_items.append(_w)
            self.scene().addItem(_w)

    def remove_item(self, widget):
        if not isinstance(widget, list):
            widget = [widget]
        for _w in widget:
            self.add_items.remove(_w)
            self.scene().removeItem(_w)

    def clear(self):
        self.scene().clear()
        self.add_items = []

    def _delete(self):
        for _n in self.scene().selectedItems():
            _n.delete()

    def auto_layout(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dot_exe = os.path.join(current_dir, r'graphviz\dot.exe')
        import_dot_file = os.path.join(current_dir, 'temp.dot')
        export_xdot_file = os.path.join(current_dir, 'temp.xdot')

        make_dot(self, import_dot_file)

        cmd = '"{0}" -Txdot -o "{1}" "{2}"'.format(dot_exe, export_xdot_file, import_dot_file)
        exec_subprocess(cmd)

        xdot_data, max_y = get_node_pos_from_xdot(export_xdot_file)

        os.remove(import_dot_file)
        os.remove(export_xdot_file)

        _pos = self.mapToScene(0, 0)

        animation_group = QtCore.QParallelAnimationGroup(self)
        for _n in node.Node.scene_nodes_iter(self):
            _d = xdot_data.get(_n.id)
            if _d is None:
                continue
            x = _d[0] + _pos.x()
            # yの値がなぜか反転してxdotに書き出される感じだったので自分で原点基準で反転させている
            y = (_d[1] * -1) + max_y
            y = y + _pos.y()
            animation = QtCore.QPropertyAnimation(_n, "pos", self)
            animation.setDuration(100)
            # animation.setEasingCurve(QtCore.QEasingCurve.InOutQuint)
            animation.setEndValue(QtCore.QPointF(x, y))
            animation_group.addAnimation(animation)

        self._animation_preprocess()
        animation_group.start()
        animation_group.finished.connect(self._animation_postprocess)

    def _animation_preprocess(self):
        for _l in line.TempLine.scene_lines_iter(self):
            _l.setVisible(False)
        for _l in line.Line.scene_lines_iter(self):
            _l.setVisible(False)

    def _animation_postprocess(self):
        # ラインの再描画と表示
        for _l in line.TempLine.scene_lines_iter(self):
            _l.update_path()
        for _l in line.Line.scene_lines_iter(self):
            _l.update_path()

    def _copy(self):
        pass

    def _paste(self):
        pass

    def _cut(self):
        pass

    def _undo(self):
        pass

    def _redo(self):
        pass


def get_node_pos_from_xdot(xdot_file_path):
    xdot_data = {}
    f_all = open(xdot_file_path).read()
    f_all = re.sub('\r|\n|\t', '', f_all)
    f_all = re.sub('(^.*?\{|\}$)', '', f_all)
    sp = f_all.split(';')
    # 最初の２要素と最後はノード以外なので無視
    max_y = 0
    for s in sp[2:-1]:
        node_name = re.sub(' +\[.+$', '', s)[1:-1]
        # ->の表記があるものはライン
        if '->' in node_name:
            continue
        x, y = re.sub('^.+pos="|".+$', '', s).split(',')
        xdot_data[node_name] = [float(x), float(y)]
        if max_y < float(y):
            max_y = float(y)
    return xdot_data, max_y


def make_dot(view, file_path, mode='all'):
    if mode == 'all':
        iter = node.Node.scene_nodes_iter(view)
    else:
        iter = view.scene().selectedItems()
    _data = get_node_data_for_dot(view, iter)

    if mode == 'all':
        _data.extend(get_line_data_for_dot(view))
        _data.extend(get_temp_line_data_for_dot(view))

    # ranksep:横のノード間隔　nodesep:縦のノード間隔
    dot_string = 'digraph sample{graph[rankdir = LR,nodesep=1.25,ranksep=1.5];node [shape=record,width=1.5];'
    dot_string = dot_string + '\r\n'.join(_data) + '}'

    with open(file_path, mode='w') as f:
        f.write(dot_string)


def get_temp_line_data_for_dot(view):
    data = []
    for _l in line.TempLine.scene_lines_iter(view):
        source_port = _l.source
        target_port = _l.target
        line_string = '"{0}":{1} -> "{2}":{3}'.format(source_port.node.id, source_port.name,
                                                      target_port.node.id, target_port.name)
        data.append(line_string)
    return data


def get_line_data_for_dot(view):
    data = []
    for _l in line.Line.scene_lines_iter(view):
        if not _l.isVisible():
            continue
        # ポートが閉じているときは一番上のポートから接続されていることにする
        source_port = _l.source
        if not source_port.isVisible():
            source_port = source_port.get_visible_parent_port()

        target_port = _l.target
        if not target_port.isVisible():
            target_port = target_port.get_visible_parent_port()

        line_string = '"{0}":{1} -> "{2}":{3}'.format(source_port.node.id, source_port.name,
                                                      target_port.node.id, target_port.name)
        data.append(line_string)
    return data


def get_node_data_for_dot(view, iter):
    data = []
    for _n in iter:
        port_names = []
        for _p in _n.ports:
            port_names.append('<{0}>{0}'.format(_p.name))
            if not _p.children_port_expand:
                continue
            for _pp in _p.children_ports_all_iter():
                if not _pp.check_parent_port_open():
                    continue
                port_names.append('<{0}>{0}'.format(_pp.name))
        node_string = '"{0}" [label = "{1}",height={2}];'.format(_n.id, '|'.join(port_names),
                                                                 len(port_names) * 0.5 + 0.5)
        data.append(node_string)
    return data


def exec_subprocess(cmd):
    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    devnull = open(os.devnull, "wb")
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=devnull,
        startupinfo=startupinfo)
    devnull.close()
    stdout, stderr = p.communicate()
    p.wait()

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
