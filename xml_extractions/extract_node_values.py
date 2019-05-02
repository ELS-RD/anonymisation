#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

import os

from lxml.etree import Element  # type: ignore

from xml_extractions.common_xml_parser_function import replace_none, read_xml

from typing import List, Tuple, Union, Optional, Iterator

Offset = Tuple[int, int, str]
Paragraph = Tuple[str, str, List[str], List[Offset]]


def get_person_name(node: Element) -> Optional[Tuple[str, str]]:
    """
    Extract value of node <Personne>
    :param node: <Personne> from Lxml
    :return: a tuple with the content inside the node, and the tail content
    """
    assert node.tag == "Personne"
    for t in node.iterchildren(tag="Texte"):
        return replace_none(t.text), replace_none(node.tail)
    return None


def get_paragraph_with_entities(parent_node: Element) -> Tuple[str, List[str], List[Offset]]:
    """
    Extract the entities from paragraph nodes
    :param parent_node: the one containing the others
    :return: a tupple with (paragraph text, the value of the children nodes, the offset of the values from children)
    """
    contents: list = list()

    for node in parent_node.iter():
        if node.tag == "Personne":
            person_name = get_person_name(node)
            if person_name is not None:
                name, after = person_name
                contents.append((name, "PERS"))
                contents.append((after, "after"))
        elif node.tag == "P":
            text = replace_none(node.text)
            contents.append((text, node.tag))
        elif node.tag == "Adresse":
            text = replace_none(node.text)
            tail = replace_none(node.tail)
            contents.append((text, "ADDRESS"))
            contents.append((tail, "after"))
        elif node.tag in ["Texte", "TexteAnonymise", "President", "Conseiller", "Greffier", "AvocatGeneral"]:
            pass
        else:
            raise NotImplementedError(f"Unexpected type of node: [{node.tag}], node content is [{node.text}] and is "
                                      f"part of [{node.getparent().text}]")
    clean_content = list()
    extracted_text = list()
    offset = list()
    text_current_size = 0
    for content in contents:
        current_text_item = content[0]
        current_tag_item = content[1]
        current_item_text_size = len(current_text_item)

        clean_content.append(current_text_item)
        if current_tag_item in ["PERS", "ADDRESS"]:
            offset.append((text_current_size,
                           text_current_size + current_item_text_size,
                           current_tag_item))
            extracted_text.append(current_text_item)
        text_current_size += current_item_text_size + 1

    paragraph_text = ' '.join(clean_content)
    return paragraph_text, extracted_text, offset


def get_paragraph_from_juri(case_id: str, juri_node: Element, keep_paragraph_without_annotation: bool) -> List[Paragraph]:
    """
    Extract paragraphs from node <Juri>
    :param case_id: xml
    :param juri_node: xml <Juri> node
    :param keep_paragraph_without_annotation: keep paragraph which doesn't include annotation according to Themis
    :return: a list of tuple of (paragraph text, value inside node, offset)
    """
    result = list()
    nodes = juri_node.xpath('./TexteJuri/P')
    for node in nodes:
        paragraph_text, extracted_text, offset = get_paragraph_with_entities(node)
        has_some_annotation = len(extracted_text) > 0
        if has_some_annotation:
            # TODO replace by unit test
            item_text = extracted_text[0]
            current_attribute = offset[0]
            start = current_attribute[0]
            end = current_attribute[1]
            assert item_text == paragraph_text[start:end]
        else:
            offset = list()
            extracted_text = list()

        if has_some_annotation | keep_paragraph_without_annotation:
            result.append((case_id, paragraph_text, extracted_text, offset))

    return result


def get_paragraph_from_file(path: str, keep_paragraph_without_annotation: bool, flatten: bool = True) -> Union[List[Paragraph], List[List[Paragraph]]]:
    """
    Read paragraph from a file
    :param path: path to the XML file
    :param keep_paragraph_without_annotation: keep paragraph which doesn't include annotation according to Themis
    :param flatten: whether to flatten all the paragraph of the file or group paragraph by case
    :return: a list of tupple (or a list of list of tuple) of (paragraph text, value inside node, offset)
    """
    result = list()
    tree = read_xml(path)
    nodes = tree.xpath('//Juri')
    for node in nodes:
        case_id = node.get("id")
        if flatten:
            result.extend(get_paragraph_from_juri(case_id, node, keep_paragraph_without_annotation))
        else:
            result.append(get_paragraph_from_juri(case_id, node, keep_paragraph_without_annotation))

    return result


def get_paragraph_from_folder(folder_path: str, keep_paragraph_without_annotation: bool, flatten: bool = True) -> Iterator[Union[Paragraph, List[Paragraph]]]:
    paths = os.listdir(folder_path)
    assert len(paths) > 0
    for path in paths:
        if path.endswith(".xml"):
            current_path = os.path.join(folder_path, path)
            paragraphs = get_paragraph_from_file(path=current_path,
                                                 keep_paragraph_without_annotation=keep_paragraph_without_annotation,
                                                 flatten=flatten)
            for paragraph in paragraphs:
                yield paragraph
