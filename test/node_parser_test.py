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

from resources.config_provider import get_config_default
from xml_extractions.extract_node_values import get_paragraph_with_entities, read_xml, get_paragraph_from_file

config_training = get_config_default()
xml_path = config_training["xml_unittest_file"]


def test_xml_parser():
    tree = read_xml(xml_path)
    r = tree.xpath('//TexteJuri/P')

    assert len(r) == 27

    for i in r:
        paragraph_text, extracted_text, offset = get_paragraph_with_entities(i)
        if len(extracted_text) > 0:
            item_text = extracted_text[0]
            current_attribute = offset[0]
            start = current_attribute[0]
            end = current_attribute[1]
            assert item_text == paragraph_text[start:end]


def test_get_paragraph():
    result_keep_no_annotation = get_paragraph_from_file(path=xml_path, keep_paragraph_without_annotation=True)
    result_keep_with_annotation = get_paragraph_from_file(path=xml_path, keep_paragraph_without_annotation=False)
    assert len(result_keep_no_annotation) == 27
    assert len(result_keep_with_annotation) == 3
