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

import regex

last_name_pattern = regex.compile("[A-Z\s]+$")


def get_last_name(text: str) -> str:
    """
    Extract last name from a full name
    :param text: full name
    :return: family name
    """
    result = last_name_pattern.search(text.strip())
    if result:
        return str(result.group(0)).strip()
    return ""


def get_first_last_name(text: str):
    """
    Extract first name and last name from a full name
    :param text: full name text
    :return: a tuple of string (first_name, last_name)
    """
    clean_text = text.strip()
    last_name = get_last_name(clean_text)
    first_name = clean_text[0:len(clean_text) - len(last_name)].strip() if len(last_name) > 0 else ""
    return first_name, last_name

