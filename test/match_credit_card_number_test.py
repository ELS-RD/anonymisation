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

from match_text.match_credit_card import get_credit_card_number
from xml_extractions.extract_node_values import Offset


def test_credit_card():
    credit_card_valid = "4474 2054 6736 1295"
    credit_card_invalid = "1265 157309414560"

    assert get_credit_card_number("pop " + credit_card_valid + " apres") == [Offset(4, 24, 'CREDIT_CARD')]
    assert get_credit_card_number("pop " + credit_card_invalid + " apres") == []
    assert get_credit_card_number("1234 1234 1234 1234") == []
    assert get_credit_card_number("1- 1234 1234 1234 1234") == []
    assert get_credit_card_number("1- " + credit_card_valid) == []
