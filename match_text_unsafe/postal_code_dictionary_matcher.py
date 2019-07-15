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

from match_text_unsafe.match_acora import AcoraMatcher
from resources.config_provider import get_config_default
from xml_extractions.extract_node_values import Offset


class PostalCodeCity:
    matcher = None

    def __init__(self):
        """
        Build a matcher of first name based on a French names dictionary
        """
        postal_code_city_list = list()
        config = get_config_default()
        file = config["postal_code_city"]

        with open(file) as f1:
            for line in f1.readlines():
                fields = line.split(";")
                city = fields[1].strip()
                if len(city) >= 3:
                    postal_code = fields[2].strip()
                    postal_code_city_list.append(postal_code + " " + city)
                    postal_code_city_list.append(city + " (" + postal_code + ")")
        assert len(postal_code_city_list) > 1000
        postal_code_city_list.pop(0)
        self.matcher = AcoraMatcher(list(postal_code_city_list),
                                    ignore_case=True)

    def get_matches(self, text: str) -> List[Offset]:
        """
        Find match of postal code and city names in a text
        :param text: original text
        :return: list of offsets
        """
        return self.matcher.get_matches(text=text, tag="ADDRESS")
