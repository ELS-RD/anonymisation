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

from match_text.match_lawyer import get_lawyer_name
from xml_extractions.extract_node_values import Offset


def test_extract_lawyer():
    text1 = "A la demande de Me Toto TOTO, avocat"
    assert get_lawyer_name(text1) == [Offset(19, 28, "LAWYER")]
    text2 = "Me Carine Chevalier - Kasprzak"
    assert get_lawyer_name(text2) == [Offset(3, 30, "LAWYER")]
