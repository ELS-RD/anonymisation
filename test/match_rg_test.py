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

from match_text.match_rg import MatchRg, get_rg_from_regex
from xml_extractions.extract_node_values import Offset


def test_rg_from_case_id():
    text1 = "CA-aix-en-provence-20130208-1022871-jurica"
    matcher = MatchRg(case_id=text1)
    assert matcher.get_rg_from_case_id() == "1022871"
    assert matcher.get_rg_offset_from_text(text=text1) == [Offset(28, 35, 'RG')]
    text2 = "Le numéro RG est celui-ci 102 /2871."
    assert matcher.get_rg_offset_from_text(text=text2) == [Offset(26, 35, 'RG')]


def test_rg_regex():
    assert get_rg_from_regex(" RG n° 11/17073") == [Offset(7, 15, 'RG')]
    assert get_rg_from_regex(" RG : 13/03625 D") == [Offset(6, 15, 'RG')]
    assert get_rg_from_regex("RG numéro : 12/01503") == [Offset(12, 20, 'RG')]
    assert get_rg_from_regex("N°RG: 13/03409") == [Offset(6, 14, 'RG')]
    assert get_rg_from_regex("N° 13/03409") == []
    assert get_rg_from_regex("Numéro d'inscription au répertoire général : 14/01913") == [Offset(45, 53, 'RG')]
