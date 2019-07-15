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

from match_text.match_courts import CourtName, get_juridictions
from xml_extractions.extract_node_values import Offset


def test_extract_court_name():
    text1 = "LA COUR D'APPEL D'AGEN, 1ère chambre dans l'affaire,"
    assert get_juridictions(text=text1) == [Offset(3, 22, "COURT_1")]
    text2 = "Par jugement en date du 21 janvier 2003, le tribunal correctionnel de Mulhouse a"
    assert get_juridictions(text=text2) == [Offset(44, 79, "COURT_1")]
    text3 = "COUR D'APPEL D'AIX EN PROVENCE N. TRUC"
    assert get_juridictions(text=text3) == [Offset(0, 32, "COURT_1")]
    text4 = "ARRET DE LA COUR D'APPEL D'AIX EN PROVENCE DU TRENTE AOUT"
    assert get_juridictions(text=text4) == [Offset(12, 42, "COURT_1")]
    text5 = "par le conseil de prud'hommes d'Aix en Provence après"
    assert get_juridictions(text=text5) == [Offset(7, 48, "COURT_1")]
    text6 = "par le conseil de prud'hommes d'Aix en Provence en l'an"
    assert get_juridictions(text=text6) == [Offset(7, 47, "COURT_1")]


def test_match_court_name():
    matcher = CourtName()
    text1 = "LA COUR D'Appel de Paris"
    assert matcher.get_matches(text=text1) == [Offset(3, 24, "COURT")]
