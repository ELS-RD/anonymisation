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

from match_text_unsafe.find_header_values import parse_xml_header
from resources.config_provider import get_config_default


def test_header_parser():
    config_training = get_config_default()
    xml_path = config_training["xml_unittest_file"]
    header_content = parse_xml_header(path=xml_path)
    assert len(header_content) == 1
    assert header_content['CA-aix-en-provence-20130208-1022871-jurica']['defendeur_fullname'] == ['Catherine ***REMOVED***']
