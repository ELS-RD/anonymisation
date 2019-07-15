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

from match_text.match_date import get_date
from xml_extractions.extract_node_values import Offset


def test_date():
    assert get_date("le 12 janvier 2013 !") == [Offset(3, 18, 'DATE_1')]
    assert get_date("le 12/01/2016 !") == [Offset(3, 13, 'DATE_1')]
    assert get_date("le 12 / 01/2016 !") == [Offset(3, 15, 'DATE_1')]
    assert get_date("le 12 / 01/16 !") == [Offset(3, 13, 'DATE_1')]
    assert get_date("ARRÊT DU HUIT FÉVRIER DEUX MILLE TREIZE") == [Offset(9, 39, 'DATE_1')]
    assert get_date("le 1er janvier 2013 !") == [Offset(3, 19, 'DATE_1')]
    assert get_date("le 552-4-1 !") == []
