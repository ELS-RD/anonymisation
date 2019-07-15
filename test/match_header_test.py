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

from match_text.match_header import MatchValuesFromHeaders
from match_text_unsafe.find_header_values import parse_xml_header
from resources.config_provider import get_config_default
from xml_extractions.extract_node_values import Offset


def test_match_headers_content():
    config_training = get_config_default()
    xml_path = config_training["xml_unittest_file"]
    header_content_all_cases = parse_xml_header(path=xml_path)
    case_id = list(header_content_all_cases.keys())[0]
    header_content = header_content_all_cases[case_id]
    headers_matcher = MatchValuesFromHeaders(current_header=header_content, threshold_size=3)
    matcher_partie_pp = headers_matcher.get_matcher_of_partie_pp_from_headers()

    text1 = "C'est Catherine ***REMOVED*** qui est responsable de ces faits avec M. LEON ***REMOVED***"

    assert matcher_partie_pp.get_matches(text1, "PERS") == [Offset(6, 29, "PERS")]
