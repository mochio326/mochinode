# # -*- coding: utf-8 -*-
from mochinode.vendor.Qt import QtCore, QtGui, QtWidgets
from mochinode import View
import uuid
from . import common


class View2(View):
    def __init__(self, *args, **kwargs):
        super(View2, self).__init__(*args, **kwargs)

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
        pass

    def _redo(self):
        pass

