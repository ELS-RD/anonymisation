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
from typing import List

import regex

from xml_extractions.extract_node_values import Offset

security_social_regex = regex.compile(pattern=r"(?<!\d[[:punct:] ]*)"
                                              r"\b"
                                              r"[1-47-8][\- \.]*"
                                              r"\d{2}[\- \.]*"
                                              r"[0-1]\d[\- \.]*"
                                              r"\d\w[\- \.]*"
                                              r"\d{3}[\- \.]*"
                                              r"\d{3}[\- \.]*"
                                              r"\d{2}[\- \.]*"
                                              r"\b"
                                              r"(?![[:punct:] ]*\d)",
                                      flags=regex.VERSION1 | regex.IGNORECASE)


def get_social_security_number(text: str) -> List[Offset]:
    """
    Get social security ID number offsets following pattern described in:
    http://fr.wikipedia.org/wiki/Num%C3%A9ro_de_s%C3%A9curit%C3%A9_sociale_en_France#Signification_des_chiffres_du_NIR
    Check the checksum code to avoid most of false positives
    :param text: original text
    :return: list of offset
    """
    pattern = security_social_regex.search(text)
    if pattern is not None:
        number_as_string = text[pattern.start():pattern.end()]
        if check_social_number_key(number_as_string):
            return [Offset(pattern.start(), pattern.end(), "SOCIAL_SECURITY_NUMBER")]

    return []


def check_social_number_key(number: str)-> bool:
    """
    Check social security number key
    Fornula there: http://marlot.org/util/calcul-de-la-cle-nir.php
    http://therese.eveilleau.pagesperso-orange.fr/pages/truc_mat/textes/cles.htm
    :param number:
    :return: True if control key is Ok
    """
    cleaned_number = ''.join(filter(lambda x: x.isdigit(), number))
    if len(cleaned_number) != 15:
        return False
    nir = int(cleaned_number[0:13])
    key = int(cleaned_number[-2:])

    return 97 - (nir % 97) == key
