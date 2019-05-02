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

from spacy.tokens.doc import Doc

from match_text_unsafe.build_entity_dictionary import EntityTypename
from misc.convert_to_bilou import convert_unknown_bilou, convert_unknown_bilou_bulk, no_action_bilou
from ner.model_factory import get_empty_model
import pytest

pytest.nlp = get_empty_model(load_labels_for_training=True)


def test_bilou_conv():
    doc: Doc = pytest.nlp.make_doc("Ceci est un test.")
    offset1 = [(5, 8, "UNKNOWN")]
    assert convert_unknown_bilou(doc, offsets=offset1).ner == ['O', '-', 'O', 'O', 'O']
    assert convert_unknown_bilou_bulk([doc], [offset1])[0].ner == ['O', '-', 'O', 'O', 'O']
    offset2 = [(5, 8, "PERS")]
    assert convert_unknown_bilou(doc, offsets=offset2).ner == ['O', 'U-PERS', 'O', 'O', 'O']
    offset3 = [(0, 4, "UNKNOWN")]
    assert convert_unknown_bilou(doc, offsets=offset3).ner == ['-', 'O', 'O', 'O', 'O']


def test_build_entity_dict():
    doc: Doc = pytest.nlp.make_doc("Ceci est un test.")
    span_doc = doc.char_span(5, 8, label="UNKNOWN")
    doc.ents = [span_doc]
    entity_typename = EntityTypename()
    entity_typename.add_spacy_entities(doc)
    assert entity_typename.get_dict() == {'est': 'UNKNOWN'}
