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

extract_lawyer = regex.compile(r"(?<=(Me|Me\.|(M|m)a(i|î)tre|M°) )"
                               r"[A-ZÉÈ]+[\w-']*"
                               r"( [A-ZÉÈ\-]+[\w-']*)*",
                               flags=regex.VERSION1)


def get_lawyer_name(text: str) -> List[Offset]:
    """
    Extract lawyer name from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    return [Offset(t.start(), t.end(), "LAWYER") for t in extract_lawyer.finditer(text)]

