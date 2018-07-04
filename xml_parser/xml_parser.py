# https://github.com/explosion/spaCy/issues/1530
import lxml
from lxml import etree


def read_xml(xml_path):
    return etree.parse(xml_path)


def replace_none(s: str) -> str:
    if s is None:
        return ""
    return s.strip()


def get_person_name(node: lxml.etree._Element)-> tuple:
    assert node.tag == "Personne"
    for t in node.iterchildren(tag="Texte"):
        return replace_none(t.text), replace_none(node.tail)


def get_paragraph_text(parent_node: lxml.etree._Element) -> tuple:
    contents: list = list()

    for node in parent_node.iter():
        if node.tag == "Personne":
            name, after = get_person_name(node)
            contents.append((name, node.tag))
            contents.append((after, "after"))
        elif node.tag in ["P", "Adresse"]:
            text = replace_none(node.text)
            contents.append((text, node.tag))
        elif node.tag in ["Texte", "TexteAnonymise"]:
            pass
        else:
            raise NotImplementedError("Unexpected type of node: [" + node.tag + "]")
    clean_content = list()
    attributes = list()
    text_current_size = 0
    for content in contents:
        current_text_item = content[0]
        current_tag_item = content[1]
        curent_item_text_size = len(current_text_item)

        clean_content.append(current_text_item)
        if current_tag_item in ["Personne", "Adresse"]:
            attributes.append((current_text_item,
                               current_tag_item,
                               text_current_size,
                               text_current_size + curent_item_text_size))
        text_current_size += curent_item_text_size + 1

    return ' '.join(clean_content), attributes


