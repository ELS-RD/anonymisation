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

from match_text.match_licence_plate import get_licence_plate


def test_licence_plate():
    assert get_licence_plate("AA111AA") == [(0, 7, 'LICENCE_PLATE')]
    assert get_licence_plate("AA-111-AA") == [(0, 9, 'LICENCE_PLATE')]
    assert get_licence_plate("AA 111 AA") == [(0, 9, 'LICENCE_PLATE')]
    assert get_licence_plate("1 AA111AA") == []
    assert get_licence_plate("AA 111 AA 1") == []

    assert get_licence_plate("1AA11") == [(0, 5, 'LICENCE_PLATE')]
    assert get_licence_plate("9999 ZZZ 99") == [(0, 11, 'LICENCE_PLATE')]
    assert get_licence_plate("9999 ZZZ 999") == []
