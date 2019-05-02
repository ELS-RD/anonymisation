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

extract_clerk_pattern_1 = regex.compile(r"(?<=(m|M) |(m|M). |(m|M)me |(m|M)me. |(m|M)onsieur |(m|M)adame | )"
                                        r"("
                                        r"(?!Conseil|Présid|Magistrat|Mme|M |Madame|Monsieur)"
                                        r"[A-ZÉÈ]+[\w-']*\s*)+(?=.{0,20}"
                                        r"(greffier|Greffier|GREFFIER|greffière|Greffière|GREFFIERE))",
                                        flags=regex.VERSION1)

extract_clerk_pattern_2 = regex.compile(r"(?<=(Greffi|greffi|GREFFI)[^:]{0,50}:.{0,10})"
                                        r"((?!Madame |Monsieur |M. |Mme. |M |Mme )[A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*)+",
                                        flags=regex.VERSION1)


def get_clerk_name(text: str) -> list:
    """
    Extract clerk name from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result1 = [(t.start(), t.end(), "JUDGE_CLERK_1") for t in extract_clerk_pattern_1.finditer(text)]
    result2 = [(t.start(), t.end(), "JUDGE_CLERK_1") for t in extract_clerk_pattern_2.finditer(text)]
    return result1 + result2

