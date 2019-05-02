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

from random import seed

from modify_text.change_case import get_title_case, random_case_change, lower_randomly_word_case
from modify_text.modify_strings import remove_org_type, remove_key_words


def test_remove_corp_name():
    assert remove_org_type("SA Toto") == "Toto"
    assert remove_org_type("SA Toto Titi") == "Toto Titi"


def test_title_case():
    assert get_title_case("mic ben toto") == "Mic Ben Toto"


def test_random_case_change():
    text = "La Banque est fermée"
    offsets = [(3, 9, "PERS")]
    seed(123)
    results = [random_case_change(text, offsets, 100) for _ in range(1, 500)]
    assert "La Banque est fermée" in results
    assert "La banque est fermée" in results
    assert "La BANQUE est fermée" in results


def test_random_lower_case_word_level():
    seed(123)
    text = "La Banque est Fermée"
    results = [lower_randomly_word_case(text) for _ in range(1, 500)]
    assert "la banque est Fermée" in results
    assert "La banque est Fermée" in results
    assert "la Banque est Fermée" in results
    assert "La Banque est Fermée" in results
    assert "la Banque est fermée" not in results


def test_remove_key_words():
    text1 = "Ayant pour conseil Me Myriam MASSENGO LACAVE et Me Toto TITI, " \
           "avocat au barreau de PARIS, toque: B1132"
    offsets1 = [(22, 44, "LAWYER"), (51, 60, "LAWYER")]
    assert remove_key_words(text=text1, offsets=offsets1, rate=100) == ('Ayant pour conseil Myriam MASSENGO LACAVE '
                                                                      'et Toto TITI, avocat au barreau de PARIS, '
                                                                      'toque: B1132',
                                                                      [(19, 41, "LAWYER"),
                                                                       (45, 54, "LAWYER")])

    assert remove_key_words(text=text1, offsets=offsets1, rate=0) == (text1, offsets1)
    # check that no word related to companies is removed
    text2 = "Condamne la SCI CEK PARTICIPATIONS à payer à la SARL CEK LOISIRS la somme de 2.000 euros."
    offsets2 = [(12, 34, 'ORGANIZATION'), (48, 64, 'ORGANIZATION')]
    assert remove_key_words(text=text2, offsets=offsets2, rate=100) == (text2, offsets2)
