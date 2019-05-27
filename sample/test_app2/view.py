# # -*- coding: utf-8 -*-
from mochinode.vendor.Qt import QtCore, QtGui, QtWidgets
from mochinode import View
import uuid
from . import common


class View2(View):
    def __init__(self, *args, **kwargs):
        self._current_operation_history = 0
        self._operation_history = [None]
        super(View2, self).__init__(*args, **kwargs)

    def add_node_on_center(self, node):
        super(View2, self).add_node_on_center(node)
        node.port_expanded.connect(self.create_history)
        node.pos_changed.connect(self.create_history)
        node.port_connect_changed.connect(self.create_history)

    def mouseReleaseEvent(self, event):
        super(View2, self).mouseReleaseEvent(event)

        if event.button() == QtCore.Qt.RightButton:
            menu = QtWidgets.QMenu()
            save = menu.addAction('save')
            load = menu.addAction('load')
            selected_action = menu.exec_(event.globalPos())

            if selected_action == save:
                common.scene_save(self)
            if selected_action == load:
                common.scene_load(self)

    def auto_layout(self):
        super(View2, self).auto_layout()
        self.create_history()

    def _delete(self):
        super(View2, self)._delete()
        self.create_history()

    def _copy(self):
        self._clipboard = {}
        self._paste_offset = 0
        selected_nodes = self.scene().selectedItems()
        related_lines = common.get_lines_related_with_node(selected_nodes, self)
        self._clipboard = common.get_save_data(selected_nodes, related_lines)

    def _paste(self):
        if self._clipboard is None:
            return
        self._paste_offset = self._paste_offset + 1

        # 貼り付け前に保存データ内のノードIDを変更することでIDの重複を避ける
        id_change_dict = {}
        for _n in self._clipboard['node']:
            new_id = str(uuid.uuid4())
            id_change_dict[_n['id']] = new_id
            _n['id'] = new_id
            _n['z_value'] = _n['z_value'] + self._paste_offset
            _n['x'] = _n['x'] + self._paste_offset * 10
            _n['y'] = _n['y'] + self._paste_offset * 10
        for _l in self._clipboard['line']:
            if id_change_dict.get(_l['source']['node_id']) is not None:
                _l['source']['node_id'] = id_change_dict.get(_l['source']['node_id'])
            if id_change_dict.get(_l['target']['node_id']) is not None:
                _l['target']['node_id'] = id_change_dict.get(_l['target']['node_id'])

        nodes = common.load_save_data(self._clipboard, self)
        self.scene().clearSelection()
        for _n in nodes:
            _n.setSelected(True)
        self.scene().update()

    def _cut(self):
        pass

    def _undo(self):
        self._undo_redo_base('undo')

    def _redo(self):
        self._undo_redo_base('redo')

    def create_history(self):
        data = common.get_save_data_from_scene_all(self)
        # Undo Redo用の操作
        if self._current_operation_history > 0:
            del self._operation_history[0:self._current_operation_history]
        self._operation_history.insert(0, data)
        self._current_operation_history = 0

    def _undo_redo_base(self, type_):
        _add = 1 if type_ == 'undo' else -1
        if self._current_operation_history >= len(self._operation_history) - _add:
            return
        if self._current_operation_history + _add < 0:
            return
        self._current_operation_history = self._current_operation_history + _add
        data = self._operation_history[self._current_operation_history]
        self.clear()
        common.load_save_data(data, self)

