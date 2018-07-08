import os
from lxml import etree


def read_xml(xml_path: str):
    """
    Parse XML file
    :param xml_path: path to the XML file
    :return: root node
    """
    if os.path.exists(xml_path):
        return etree.parse(xml_path)
    else:
        raise IOError("File [" + xml_path + "] doesn't exist!")


def replace_none(s: str) -> str:
    """
    Replace NONE by an empty string
    :param s: original string which may be NONE
    :return: a stripped string, empty if NONE
    """
    if s is None:
        return ""
    return s.strip()
