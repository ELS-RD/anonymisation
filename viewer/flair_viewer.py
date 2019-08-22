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
import html
from typing import Union, List
from flair.data import Sentence

colors = {"PERS": "#ff9933",  # orange
          "PHONE_NUMBER": "#ff9933",
          "LICENCE_PLATE": "#ff9933",
          # "SOCIAL_SECURITY_NUMBER": "#ff9933",
          "ADDRESS": "#ff99cc",  # pink
          "ORGANIZATION": "#00ccff",  # blue
          "LAWYER": "#ccffcc",  # light green
          "JUDGE_CLERK": "#ccccff",  # purple
          "COURT": "#ccffff",  # light blue
          "RG": "#99ff99",  # green
          "DATE": "#ffcc99",  # salmon
          "BAR": "#ffe699",  # light yellow
          "UNKNOWN": "#ff0000"}  # red
