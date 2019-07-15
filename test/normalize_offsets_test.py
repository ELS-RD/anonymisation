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

from match_text.match_doubtful_mwe import MatchDoubfulMwe
from misc.normalize_offset import normalize_offsets, remove_spaces_included_in_offsets, \
    clean_offsets_from_unwanted_words, remove_tag_priority_info
from xml_extractions.extract_node_values import Offset


def test_normalize_offsets():
    data1 = [Offset(5, 10, "LAWYER"), Offset(18, 24, "ORGANIZATION"), Offset(22, 24, "ORGANIZATION"), Offset(120, 133, "LAWYER")]
    assert normalize_offsets(data1) == [Offset(5, 10, "LAWYER"), Offset(18, 24, "ORGANIZATION"), Offset(120, 133, "LAWYER")]
    data2 = [Offset(71, 75, "PERS"), Offset(76, 85, "PERS")]
    assert normalize_offsets(data2) == [Offset(71, 85, "PERS")]
    data3 = [Offset(5, 10, "LAWYER"), Offset(71, 75, "PERS"), Offset(76, 85, "PERS"), Offset(120, 133, "LAWYER")]
    assert normalize_offsets(data3) == [Offset(5, 10, "LAWYER"), Offset(71, 85, "PERS"), Offset(120, 133, "LAWYER")]
    data4 = [Offset(5, 10, "LAWYER"), Offset(77, 85, "PERS"), Offset(77, 85, "PERS"), Offset(120, 133, "LAWYER")]
    assert normalize_offsets(data4) == [Offset(5, 10, "LAWYER"), Offset(77, 85, "PERS"), Offset(120, 133, "LAWYER")]
    data5 = [Offset(16, 20, "PERS"), Offset(21, 30, "PERS")]
    assert normalize_offsets(data5) == [Offset(16, 30, "PERS")]
    data6 = [Offset(10, 21, "PERS"), Offset(22, 30, "PERS")]
    assert normalize_offsets(data6) == [Offset(10, 30, "PERS")]
    data7 = []
    assert normalize_offsets(data7) == []
    data8 = [Offset(1, 1, "PERS")]
    assert normalize_offsets(data8) == []
    data9 = [Offset(1, 3, "PERS")]
    assert normalize_offsets(data9) == []
    data10 = [Offset(1, 10, "PERS"), Offset(1, 10, "PERS"), Offset(3, 10, "PERS")]
    assert normalize_offsets(data10) == [Offset(1, 10, "PERS")]
    data11 = [Offset(0, 34, "ORGANIZATION"), Offset(0, 8, "ORGANIZATION")]
    assert normalize_offsets(data11) == [Offset(0, 34, "ORGANIZATION")]
    data12 = [Offset(1, 10, "PERS"), Offset(1, 10, "ORGANIZATION_1")]
    assert normalize_offsets(data12) == [Offset(1, 10, "ORGANIZATION")]
    data13 = [Offset(1, 10, "PERS"), Offset(5, 10, "ORGANIZATION_1")]
    assert normalize_offsets(data13) == [Offset(1, 10, "ORGANIZATION")]
    data14 = [Offset(21, 33, "DATE"), Offset(35, 55, "PERS")]
    assert normalize_offsets(data14) == data14


def test_remove_spaces():
    text = "Je suis ici et je programme."
    offset = [Offset(3, 8, "TEST")]
    span_original = text[offset[0].start:offset[0].end]
    assert span_original == "suis "
    new_offset = remove_spaces_included_in_offsets(text, offset)
    span_new = text[new_offset[0].start:new_offset[0].end]
    assert span_new == span_original.strip()


def test_remove_tag_priority_info():
    assert remove_tag_priority_info("PERS_1") == "PERS"


def test_remove_unwanted_words():
    text1 = "Monsieur toto"
    offset1 = [Offset(0, len("Monsieur toto"), "PERS")]
    assert clean_offsets_from_unwanted_words(text=text1, offsets=offset1) == [Offset(9, 13, "PERS")]
    text2 = "Succombant même partiellement, Madame GUERIN supportera la charge "
    offset2 = [Offset(31, 37, "PERS"), Offset(31, 44, "PERS")]
    assert clean_offsets_from_unwanted_words(text=text2, offsets=offset2) == [Offset(37, 37, "PERS"),
                                                                              Offset(38, 44, "PERS")]


def test_generate_and_clean_unknown_label():
    text1 = "Michaël et Jessica se baladent sur les bords de la Seine."
    matcher = MatchDoubfulMwe()
    expected_offset = [Offset(0, 7, 'UNKNOWN'), Offset(11, 18, 'UNKNOWN')]
    assert matcher.get_all_unknown_words_offsets(text=text1) == expected_offset
    offset1 = [Offset(0, 7, "PERS")]
    assert matcher.clean_unknown_offsets(expected_offset + offset1) == [Offset(0, 7, "PERS"), Offset(11, 18, 'UNKNOWN')]
    assert matcher.get_unknown_words_offsets(text=text1, offsets=offset1) == [Offset(0, 7, "PERS"), Offset(11, 18, 'UNKNOWN')]
    offset2 = [Offset(11, 18, "PERS")]
    assert matcher.clean_unknown_offsets(expected_offset + offset2) == [Offset(0, 7, 'UNKNOWN'), Offset(11, 18, "PERS")]
    assert matcher.get_unknown_words_offsets(text=text1, offsets=offset2) == [Offset(0, 7, 'UNKNOWN'), Offset(11, 18, "PERS")]
    offset3 = [Offset(3, 9, "PERS")]
    assert matcher.clean_unknown_offsets(expected_offset + offset3) == [Offset(3, 9, "PERS"), Offset(11, 18, 'UNKNOWN')]
    assert matcher.get_unknown_words_offsets(text=text1, offsets=offset3) == [Offset(3, 9, "PERS"), Offset(11, 18, 'UNKNOWN')]
    offset4 = [Offset(3, 12, "PERS")]
    assert matcher.clean_unknown_offsets(expected_offset + offset4) == offset4
    assert matcher.get_unknown_words_offsets(text=text1, offsets=offset4) == offset4
    offset4 = [Offset(2, 5, "PERS")]
    assert matcher.clean_unknown_offsets(expected_offset + offset4) == [Offset(2, 5, "PERS"), Offset(11, 18, 'UNKNOWN')]
    text2 = "C'est pourquoi Madame Toto souhaite obtenir le divorce."
    assert matcher.get_all_unknown_words_offsets(text=text2) == [Offset(22, 26, 'UNKNOWN')]
