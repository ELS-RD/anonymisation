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

barreau_pattern = regex.compile(r"barreau ((?i)de |d'|du )"
                                r"[A-ZÉÈ'\-]+\w*"
                                r"( (en |de |et les |du )?[A-Z'\-]+\w*)*",
                                flags=regex.VERSION1)


def get_bar(text: str) -> List[Offset]:
    """
    Extract offset related to a bar and its city localization
    French bar list: http://www.conferencedesbatonniers.com/barreaux/userslist/7-liste-des-barreaux
    :param text: original text
    :return: offset as a list
    """
    return [Offset(t.start(), t.end(), "BAR_1") for t in barreau_pattern.finditer(text)]
