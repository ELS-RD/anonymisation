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

import os

from lxml import etree


def read_xml(xml_path: str):
    """
    Parse XML file
    :param xml_path: path to the XML file
    :return: root node
    """
    if os.path.exists(xml_path):
        return etree.parse(xml_path)
    else:
        raise IOError("File [" + xml_path + "] doesn't exist!")


def replace_none(s: str) -> str:
    """
    Replace NONE by an empty string
    :param s: original string which may be NONE
    :return: a stripped string, empty if NONE
    """
    if s is None:
        return ""
    return s.strip()
