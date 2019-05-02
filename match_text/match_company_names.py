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

from modify_text.modify_strings import org_types

find_corp = regex.compile("(((?i)" + org_types + r") "
                                                 r"((?i)"
                                                 r"(de |le |la |les |pour |l'|et |en |des |d'|au |du )"
                                                 r")*"
                                                 r"((\()?[A-ZÉÈ&']+[\w\-'\.\)]*)"
                                                 r"( (de |le |la |les |pour |l'|et |en |des |d'|au |du |\(|& |/ ?|\- ?)*"
                                                 r"[A-ZÉÈ\-&']+[\w\-'\.\)]*"
                                                 r")*"
                                                 r")", flags=regex.VERSION1)


def get_company_names(text: str) -> list:
    """
    Extract company names from string text
    :param text: original text
    :return: a list of offsets
    """
    return [(t.start(), t.end(), "ORGANIZATION_1") for t in find_corp.finditer(text)]
