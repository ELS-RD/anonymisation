import lxml
from lxml import etree

from xml_parser.common_xml_parser_function import replace_none, read_xml


def get_person_name(node: lxml.etree._Element) -> tuple:
    """
    Extract value of node <Personne>
    :param node: <Personne> from Lxml
    :return: a tuple with the content inside the node, and the tail content
    """
    assert node.tag == "Personne"
    for t in node.iterchildren(tag="Texte"):
        return replace_none(t.text), replace_none(node.tail)


def get_paragraph_with_entities(parent_node: lxml.etree._Element) -> tuple:
    """
    Extract the entities from paragraph nodes
    :param parent_node: the one containing the others
    :return: a tupple with (paragraph text, the value of the children nodes, the offset of the values from children)
    """
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
    extracted_text = list()
    offset = list()
    text_current_size = 0
    for content in contents:
        current_text_item = content[0]
        current_tag_item = content[1]
        current_item_text_size = len(current_text_item)

        clean_content.append(current_text_item)
        if current_tag_item in ["Personne", "Adresse"]:
            offset.append((text_current_size,
                           text_current_size + current_item_text_size,
                           current_tag_item))
            extracted_text.append(current_text_item)
        text_current_size += current_item_text_size + 1

    paragraph_text = ' '.join(clean_content)
    return paragraph_text, extracted_text, {'entities': offset}


def get_paragraph_from_file(path: str, spacy_format: bool, keep_paragraph_without_annotation: bool) -> list:
    """
    Read paragraph from a file
    :param path: path to the XML file
    :param spacy_format: if True, don't include value content
    :param keep_paragraph_without_annotation: keep paragraph which doesn't include annotation according to Themis
    :return: a tupple of (paragraph text, value inside node, offset) OR (paragraph text, offset)
    """
    result = list()
    tree = read_xml(path)
    nodes = tree.xpath('//TexteJuri/P')
    for node in nodes:
        paragraph_text, extracted_text, offset = get_paragraph_with_entities(node)
        has_some_annotation = len(extracted_text) > 0
        if has_some_annotation:
            item_text = extracted_text[0]
            current_attribute = offset.get('entities')[0]
            start = current_attribute[0]
            end = current_attribute[1]
            assert item_text == paragraph_text[start:end]
        else:
            offset = list()
            extracted_text = list()

        if spacy_format & (has_some_annotation | keep_paragraph_without_annotation):
            result.append((paragraph_text, offset))
        elif has_some_annotation | keep_paragraph_without_annotation:
            result.append((paragraph_text, extracted_text, offset))

    return result
