# # -*- coding: utf-8 -*-
from mochinode.vendor.Qt import QtCore, QtGui, QtWidgets
from mochinode import Node, Port
import xml.etree.ElementTree as ET
import re
import os
import glob


def get_node_file_list():
    path = get_xml_dir()
    for f in glob.glob(r'{}\*.xml'.format(path)):
        yield f


def get_xml_dir():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(os.path.join(base, 'node_db'))
    return path


class PortColor(object):
    Int = QtCore.Qt.red
    Bool = QtCore.Qt.green

    def __setattr__(self, *_):
        pass


class XmlNode(Node):
    def __init__(self, name='', label='node', xml_code=''):
        self.code = xml_code
        self.recalculation_weight = 0

        super(XmlNode, self).__init__(name=name, label=label)

    def update_recalculation_weight(self):
        _source_nodes = self.get_source_nodes()
        self.recalculation_weight = len(_source_nodes)

    def propagation_port_value(self):
        for _p in self.children_ports_all_iter():
            if _p.type == 'in':
                if len(_p.lines) > 0:
                    _p.value = _p.lines[0].source.value

    def recalculation(self):
        code_str = self.code.replace('{{', 'self.port["').replace('}}', '"]')
        exec (code_str)
        # super(XmlNode, self).recalculation()
        self.update()

    # def update(self):
    #     for _p in self.children_ports_all_iter():
    #         _p.label.label = str(_p.value)
    #         _p.label.update()
    #     super(XmlNode, self).update()


def create_node_for_xml(xml_file='', view=None):
    _dir = get_xml_dir()
    tree = ET.parse('{}\{}.xml'.format(_dir, xml_file))
    n = XmlNode(name=xml_file, label=tree._root.attrib['Label'], xml_code=format_code(tree.find('Code').text))
    p = tree.findall('Port')
    create_ports_for_xml(p, n, view)
    n.deploying_port()
    return n


# xmlに記述された実行コードの先頭の空白を削除する
def format_code(code):
    code = code.split('\n')
    match_end = None
    for i, c in enumerate(code):
        if c.strip() == '':
            continue
        m = re.match('^ +', c)
        if match_end is None:
            if m is None:
                match_end = 0
            else:
                match_end = m.end()
        if len(c) > match_end:
            code[i] = c[match_end:]

    return '\n'.join(code)


def create_ports_for_xml(ports_xml, parent, view):
    port_color = PortColor()
    for _p in ports_xml:
        _value_type = _p.attrib.get('ValueType')
        _def_value = _p.attrib.get('DefaultValue')
        if _value_type == 'Int':
            _def_value = int(_def_value)
        elif _value_type == 'Bool':
            _def_value = bool(_def_value)

        if isinstance(parent, XmlNode):
            pp = parent.add_port(label=_p.attrib.get('Label'), port_type=_p.attrib.get('Type'),
                                 color=getattr(port_color, _value_type),
                                 value_type=_value_type, value=_def_value)
        else:
            pp = Port(parent=parent, label=_p.attrib.get('Label'), port_type=_p.attrib.get('Type'),
                      color=getattr(port_color, _value_type), value_type=_value_type,
                      value=_def_value)
        _p_find = _p.findall('Port')
        create_ports_for_xml(_p_find, pp, view)
