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

from match_text.match_extension_of_entity_name import get_all_name_variation
from match_text.match_first_name_dictionary import FirstName
from xml_extractions.extract_node_values import Offset


def test_match_sub_pattern():
    texts = ["Je suis avec Jessica BENESTY et elle est sympa.",
             "Jessica n'est pas là.",
             "Ou est Mme. Benesty ?",
             "La SARL TOTO forme avec la SCI TOTO un groupe de sociétés.",
             "Condamné CEK PARTICIPATIONS à payer à la SCI CEK PARTICIPATIONS la somme"]
    offsets = [[Offset(13, 28, "PERS")], [], [], [Offset(3, 12, "ORGANIZATION")], [Offset(41, 63, "ORGANIZATION")]]
    assert get_all_name_variation(texts, offsets, threshold_span_size=4) == [[Offset(13, 20, "PERS"),
                                                                              Offset(13, 28, "PERS"),
                                                                              Offset(21, 28, "PERS"),
                                                                              Offset(13, 28, "PERS")],
                                                                             [Offset(0, 7, "PERS")],
                                                                             [Offset(12, 19, "PERS")],
                                                                             [Offset(3, 12, "ORGANIZATION"),
                                                                              Offset(8, 12, "ORGANIZATION"),
                                                                              Offset(31, 35, "ORGANIZATION"),
                                                                              Offset(3, 12, "ORGANIZATION")],
                                                                             [Offset(9, 27, "ORGANIZATION"),
                                                                              Offset(41, 63, "ORGANIZATION"),
                                                                              Offset(45, 63, "ORGANIZATION"),
                                                                              Offset(41, 63, "ORGANIZATION")]]


def test_get_first_name_dict():
    matcher = FirstName(ignore_case=False)
    assert len(matcher.first_name_dict) == 12464
    assert "Michaël" in matcher.first_name_dict


def test_get_phrase_matcher():
    text = "Aujourd'hui, Michaël et Jessica écrivent des unit tests dans la joie et la bonne humeur, " \
           "mais où sont donc les enfants ?"
    matcher = FirstName(ignore_case=False)
    assert matcher.get_matches(text=text) == [Offset(13, 19, "PERS"), Offset(24, 30, "PERS")]
    assert matcher.contain_first_names(text=text) is True

