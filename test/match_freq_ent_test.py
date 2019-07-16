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

from match_text_unsafe.build_dict_from_recognized_entities import FrequentEntities
from xml_extractions.extract_node_values import Offset


def test_frequent_entities():
    freq_entities = {"benesty": "LAWYER", "jessica": "PERS"}
    frequent_entities_matcher = FrequentEntities.test_builder(content=freq_entities)
    text = "Me Benesty rencontre son client Jessica."
    assert frequent_entities_matcher.get_matches(text=text) == [Offset(3, 10, "LAWYER"), Offset(32, 39, "PERS")]
