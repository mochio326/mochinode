# # -*- coding: utf-8 -*-
import json
import os
from mochinode.vendor.Qt import QtCore, QtGui, QtWidgets
from mochinode import Node, View, Port, Line
from . import node

def get_line_save_data(l):
    data = {}
    data['source'] = {}
    data['source']['node_id'] = l.source.node.id
    data['source']['port_name'] = l.source.name
    data['target'] = {}
    data['target']['node_id'] = l.target.node.id
    data['target']['port_name'] = l.target.name
    return data


def get_node_save_data(n):
        data = {}
        data['id'] = n.id
        data['name'] = n.name
        data['z_value'] = n.zValue()
        data['x'] = n.x()
        data['y'] = n.y()
        data['ports'] = {}
        for _p in n.ports:
            data['ports'][_p.name] = {}
            data['ports'][_p.name]['expand'] = _p.children_port_expand
            data['ports'][_p.name]['value'] = _p.value
            for _pp in _p.children_ports_all_iter():
                data['ports'][_pp.name] = {}
                data['ports'][_pp.name]['expand'] = _pp.children_port_expand
                data['ports'][_pp.name]['value'] = _pp.value
        return data


def create_node_for_save_data(view, save_data):
    _n = node.create_node_for_xml(save_data['name'], view)
    view.add_item(node)
    load_node_data(_n, save_data, False)

def load_node_data(node, save_data, ports_only=False):
    for _p in node.children_ports_all_iter():
        _p.children_port_expand = save_data['ports'][_p.name]['expand']
        _p.value = save_data['ports'][_p.name]['value']
    node.deploying_port()
    if ports_only:
        return
    node.id = save_data['id']
    node.setZValue(save_data['z_value'])
    node.setX(save_data['x'])
    node.setY(save_data['y'])
    node.update()


def scene_save(view):
    save_data = get_save_data_from_scene_all(view)
    not_escape_json_dump(r'c:\temp\node_tool.json', save_data)


def get_save_data_from_scene_all(view):
    nodes = [_n for _n in Node.scene_nodes_iter(view)]
    lines = [_l for _l in Line.scene_lines_iter(view)]
    return get_save_data(nodes, lines)


def get_save_data(nodes, lines):
    save_data = {}
    save_data['node'] = [get_node_save_data(_n) for _n in nodes]
    save_data['line'] = [get_line_save_data(_l) for _l in lines]
    return save_data


def nodes_recalculation(view):

    recalculation_nodes = []

    for _n in Node.scene_nodes_iter(view):
        _n.update_recalculation_weight()
        # if _n.forced_recalculation:
        recalculation_nodes.append(_n)

    # recalculation_weightを基準に並び替え
    recalculation_nodes = sorted(recalculation_nodes, key=lambda n: n.recalculation_weight)

    for i, _n in enumerate(recalculation_nodes):
        _n.propagation_port_value()
        _n.recalculation()
        _n.update()


def load_save_data(data, view):
    if data is None:
        return
    nodes = []
    for _n in data['node']:
        _n2 = node.create_node_for_xml(_n['name'], view)
        view.add_node_on_center(_n2)
        load_node_data(_n2, _n, False)
        nodes.append(_n2)

    for _l in data['line']:
        line_connect_for_save_data(_l, view)

    for _n in nodes:
        for _p in _n.children_ports_all_iter():
            _p.create_temp_line()

    # nodes_recalculation(view)
    return nodes


def scene_load(view):
    data = not_escape_json_load(r'c:\temp\node_tool.json')
    view.clear()
    load_save_data(data, view)
    view.scene().update()


def line_connect_for_save_data(line_data, view):
    for _n in Node.scene_nodes_iter(view):
        if line_data['source']['node_id'] == _n.id:
            source = _n.port[line_data['source']['port_name']]
        if line_data['target']['node_id'] == _n.id:
            target = _n.port[line_data['target']['port_name']]
    new_line = Line(QtCore.QPointF(0, 0), QtCore.QPointF(0, 0), target.color)
    source.connect_line(new_line)
    target.connect_line(new_line)
    view.add_item(new_line)


def get_lines_related_with_node(nodes, view):
    # 指定ノードに関連するラインをシーン内から取得
    nodes_id = [_n.id for _n in nodes]
    related_lines = []
    for _l in Line.scene_lines_iter(view):
        if _l.source.node.id in nodes_id and _l.target.node.id in nodes_id:
            related_lines.append(_l)
    return related_lines


def not_escape_json_dump(path, data):
    # http://qiita.com/tadokoro/items/131268c9a0fd1cf85bf4
    # 日本語をエスケープさせずにjsonを読み書きする
    text = json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2)
    with open(path, 'w') as fh:
        fh.write(text.encode('utf-8'))


def not_escape_json_load(path):
    if os.path.isfile(path) is False:
        return None
    with open(path) as fh:
        data = json.loads(fh.read(), "utf-8")
    return data
