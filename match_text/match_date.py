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

un_trent_et_un = ["un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf",
                  "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix.sept", "dix.huit",
                  "dix.neuf", "vingt", "vingt.et.un", "vingt.deux", "vingt.trois", "vingt.quatre",
                  "vint.cinq", "vingt.six", "vingt.sept", "vingt.huit", "vingt.neuf", "trente", "trente.et.un"]

years = ["mille.neuf.cent.quatre.vingts(.et)?", "deux.mille"]

months = ["janvier", "f.vrier", "mars", "avril", "mai", "juin", "juillet", "ao.t",
          "septembre", "octobre", "novembre", "d.cembre"]


def get_or_regex(original_list: List[str]) -> str:
    """
    Transform a list of string to a [OR] regex
    :param original_list:
    :return: string to insert in a regex
    """
    return '|'.join(original_list)


date_pattern_in_letters = "(" + get_or_regex(un_trent_et_un) + ") (" + get_or_regex(months) + ") (" + \
                          get_or_regex(years) + "." + "(" + get_or_regex(un_trent_et_un) + ")?)"

date_pattern_in_letters_regex = regex.compile(date_pattern_in_letters,
                                              flags=regex.VERSION1 | regex.IGNORECASE)

date_pattern_in_numbers_1 = r"[0-3]?\d( ?er)? (" + get_or_regex(months) + r") (19|20|20)?\d{2}"
date_pattern_in_numbers_regex_1 = regex.compile(date_pattern_in_numbers_1,
                                                flags=regex.VERSION1 | regex.IGNORECASE)

date_pattern_in_numbers_regex_2 = regex.compile(r'(\d{1,2}.?(/|\-).?\d{1,2}.?(/|\-).?\d{2,4})',
                                                flags=regex.VERSION1 | regex.IGNORECASE)


def get_date(text: str) -> List[Offset]:
    """
    Parse text to retrieve offset mentioning a date
    :param text: original text
    :return: offsets as a list
    """
    r1 = [Offset(t.start(), t.end(), "DATE_1") for t in date_pattern_in_letters_regex.finditer(text)]
    r2 = [Offset(t.start(), t.end(), "DATE_1") for t in date_pattern_in_numbers_regex_1.finditer(text)]
    r3 = [Offset(t.start(), t.end(), "DATE_1") for t in date_pattern_in_numbers_regex_2.finditer(text)]
    return r1 + r2 + r3
