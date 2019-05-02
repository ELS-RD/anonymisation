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

import regex

new_licence_plate_regex = regex.compile(pattern=r"(?<!(\d|[A-Z])[[:punct:] ]*)"
                                                r"\b"
                                                r"([A-Z][\- \.]*){2}"
                                                r"([1-9][\- \.]*){3}"
                                                r"([A-Z][\- \.]*){2}"
                                                r"\b"
                                                r"(?![[:punct:] ]*(\d|[A-Z]))",
                                        flags=regex.VERSION1)

old_licence_plate_regex = regex.compile(pattern=r"(?<!(\d|[A-Z])[[:punct:] ]*)"
                                                r"\b"
                                                r"([1-9]{1,4}[\- \.]*)"
                                                r"[A-Z]{2,3}[\- \.]*"
                                                r"[1-9]{2}"
                                                r"\b"
                                                r"(?![[:punct:] ]*(\d|[A-Z]))",
                                        flags=regex.VERSION1)


def get_licence_plate(text: str) -> list:
    """
    Find licence plate number following pattern described in
    https://www.developpez.net/forums/d1308588/php/langage/regex/creer-regex-plaque-d-immatriculation/
    :param text: original text
    :return: list of offsets
    """
    pattern_new = list(new_licence_plate_regex.finditer(text))
    pattern_old = list(old_licence_plate_regex.finditer(text))
    patterns = pattern_new + pattern_old
    results = list()
    for pattern in patterns:
        results.append((pattern.start(), pattern.end(), "LICENCE_PLATE"))
    return results
