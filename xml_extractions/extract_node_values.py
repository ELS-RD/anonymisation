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

from typing import List, Tuple, Optional

from attr import dataclass
from lxml.etree import Element  # type: ignore

from xml_extractions.common_xml_parser_function import replace_none, read_xml


@dataclass
class Offset:
    start: int
    end: int
    type: str

    def to_tuple(self) -> Tuple[int, int, str]:
        return self.start, self.end, self.type


@dataclass
class Paragraph:
    case_id: str
    text: str
    extracted_text: List[str]
    offsets: List[Offset]


Case = List[Paragraph]


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
    contents: List[Tuple[str, str]] = list()

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
    offsets: List[Offset] = list()
    text_current_size = 0
    for content in contents:
        current_text_item = content[0]
        current_tag_item = content[1]
        current_item_text_size = len(current_text_item)

        clean_content.append(current_text_item)
        if current_tag_item in ["PERS", "ADDRESS"]:
            offsets.append(Offset(start=text_current_size,
                                  end=text_current_size + current_item_text_size,
                                  type=current_tag_item))
            extracted_text.append(current_text_item)
        text_current_size += current_item_text_size + 1

    paragraph_text = ' '.join(clean_content)
    return paragraph_text, extracted_text, offsets


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
            start = current_attribute.start
            end = current_attribute.end
            assert item_text == paragraph_text[start:end]
        else:
            offset = list()
            extracted_text = list()

        if has_some_annotation | keep_paragraph_without_annotation:
            result.append(Paragraph(case_id, paragraph_text, extracted_text, offset))

    return result


def get_paragraph_from_file(path: str,
                            keep_paragraph_without_annotation: bool) -> List[Paragraph]:
    """
    Read paragraph from a file
    :param path: path to the XML file
    :param keep_paragraph_without_annotation: keep paragraph which doesn't include annotation according to Temis
    :return: a list of tupple (or a list of list of tuple) of (paragraph text, value inside node, offset)
    """
    result: List[Paragraph] = list()
    tree = read_xml(path)
    nodes = tree.xpath('//Juri')
    for node in nodes:
        case_id = node.get("id")
        result.extend(get_paragraph_from_juri(case_id, node, keep_paragraph_without_annotation))

    return result
