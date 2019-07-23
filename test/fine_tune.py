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
from fine_tune_pre_trained_model import recompose_paragraphs
from xml_extractions.extract_node_values import Offset


#def test_assemble():
content = [("Ceci est une phrase.", []),
           ("Ceci est une seconde phrase", [Offset(3, 6, "a")]),
           ("et ceci est la suite.", [Offset(8, 10, "a")])]
print(recompose_paragraphs(content))


content = [("Ceci est une phrase.", []),
           ("Ceci est une seconde phrase", [Offset(3, 6, "a")]),
           ("et ceci est la suite.", [Offset(8, 10, "a")]),
           ("Ceci est une phrase.", [])]
print(recompose_paragraphs(content))
