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

from match_text.match_social_security_number import get_social_security_number


def test_social_security():
    valid_id = "2 40 09 93 618 017 05"
    invalid_id = "2 40 09 93 618 017 06"
    assert get_social_security_number(valid_id) == [(0, 21, 'SOCIAL_SECURITY_NUMBER')]
    assert get_social_security_number("1" + valid_id) == []
    assert get_social_security_number(invalid_id) == []
