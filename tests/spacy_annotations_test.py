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

import pytest
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from spacy.tokens.doc import Doc

from misc.convert_to_bilou import convert_unknown_bilou, convert_unknown_bilou_bulk
from ner.model_factory import get_empty_model
from xml_extractions.extract_node_values import Offset

pytest.nlp = get_empty_model(load_labels_for_training=True)


def test_bilou_conv():
    doc: Doc = pytest.nlp.make_doc("Ceci est un test.")
    offset1 = [Offset(5, 8, "UNKNOWN")]
    assert convert_unknown_bilou(doc, offsets=offset1).ner == ["O", "-", "O", "O", "O"]
    assert convert_unknown_bilou_bulk([doc], [offset1])[0].ner == ["O", "-", "O", "O", "O"]
    offset2 = [Offset(5, 8, "PERS")]
    assert convert_unknown_bilou(doc, offsets=offset2).ner == ["O", "U-PERS", "O", "O", "O"]
    offset3 = [Offset(0, 4, "UNKNOWN")]
    assert convert_unknown_bilou(doc, offsets=offset3).ner == ["-", "O", "O", "O", "O"]


def test_tokenizer():
    doc: Doc = pytest.nlp.make_doc("Ceci est un test.")
    offsets = [(0, 4, "PERS"), (9, 11, "PERS")]
    gold: GoldParse = GoldParse(doc, entities=offsets)
    word_extracted = [doc.char_span(o[0], o[1]) for o in offsets]
    count_ent = sum([1 for item in gold.ner if item != "O"])
    assert count_ent == len(word_extracted)

    offsets = [(0, 4, "PERS"), (9, 12, "PERS")]
    gold: GoldParse = GoldParse(doc, entities=offsets)
    word_extracted = [doc.char_span(o[0], o[1]) for o in offsets if doc.char_span(o[0], o[1]) is not None]
    count_ent = sum([1 for item in gold.ner if item != "O"])
    assert count_ent > len(word_extracted)


def test_new_tokenizer():
    assert len(pytest.nlp.make_doc("ceci est un test")) == 4
    assert len(pytest.nlp.make_doc("ceci est un -test")) == 5
    assert len(pytest.nlp.make_doc("ceci est un te-st")) == 6
    assert len(pytest.nlp.make_doc("ceci est un l'test")) == 5


def test_score():
    s = "Le Président, Le Commis-Greffier, Jean-Paul I FFELLI Nelly DUBAS"
    doc: Doc = pytest.nlp.make_doc(s)
    expected_span: GoldParse = GoldParse(doc, entities=[(34, 64, "PERS")])
    predicted_span = doc.char_span(34, 58, "PERS")
    doc.ents = [predicted_span]
    score: Scorer = Scorer()
    score.score(doc, expected_span)
    assert score.ents_per_type == dict([("PERS", {"p": 0.0, "r": 0.0, "f": 0.0})])

    predicted_span = doc.char_span(34, 64, "PERS")
    doc.ents = [predicted_span]
    score: Scorer = Scorer()
    score.score(doc, expected_span)
    assert score.ents_per_type == dict([("PERS", {"p": 100.0, "r": 100.0, "f": 100.0})])


def test_set_span():
    s = "Le Président, Le Commis-Greffier, Jean-Paul I FFELLI Nelly DUBAS"
    doc1: Doc = pytest.nlp.make_doc(s)
    doc2: Doc = pytest.nlp.make_doc(s)
    span1 = doc1.char_span(34, 58, "PERS")
    span2 = doc2.char_span(34, 58, "PERS")
    assert {span1.text}.symmetric_difference({span2.text}) == set()
    assert len({span1}.symmetric_difference({span2})) > 0
