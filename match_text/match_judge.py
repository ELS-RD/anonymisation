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

extract_judge_pattern_1 = regex.compile(r"("
                                        r"(?!Madame |Monsieur|M\. |Mme\.|M |Mme|Conseil|Présid|Magistrat|Chambre)"
                                        r"[A-ZÉÈ']+[\w']*"
                                        r")"
                                        r"( (de |d')?[A-ZÉÈ\-']+[\w\-']*)*"
                                        r"(?=, "
                                        r"("
                                        r"(M|m)agistrat|"
                                        r"conseill.{0,30}(cour|président|magistrat|chambre|.{0,5}$|"
                                        r", |application des dispositions)|"
                                        r"président.+(cour|magistrat|chambre)|"
                                        r"président.{0,5}$|"
                                        r"(p|P)remier (p|P)résident|"
                                        r"Conseil.*|"
                                        r"Président.*|"
                                        r"(s|S)ubstitut)"
                                        r")",
                                        flags=regex.VERSION1)

extract_judge_pattern_2 = regex.compile(r"(?<=(?i)"
                                        r"^(magistrat|"
                                        r"conseill\w{1,3}|"
                                        r"président\w{0,3})\s+"
                                        r":.{0,20}"
                                        r")"
                                        r"((?!(?i)madame |monsieur |m. |mme. |m |mme |chambre )"
                                        r"[A-ZÉÈ]+[\w\-']*)"
                                        r"( [A-ZÉÈ\-]+[\w\-']*)*",
                                        flags=regex.VERSION1)


def get_judge_name(text: str) -> List[Offset]:
    """
    Extract judge name from text
    :param text: original paragraph text
    :return: offsets as a list
    """

    r1 = [Offset(start=t.start(), end=t.end(), type="JUDGE_CLERK_1") for t in extract_judge_pattern_1.finditer(text)]
    r2 = [Offset(start=t.start(), end=t.end(), type="JUDGE_CLERK_1") for t in extract_judge_pattern_2.finditer(text)]
    return r1 + r2

