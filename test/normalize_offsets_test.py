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


from misc.normalize_offset import normalize_offsets
from xml_extractions.extract_node_values import Offset


def test_normalize_offsets():
    data1 = [Offset(5, 10, "LAWYER"), Offset(18, 24, "ORGANIZATION"), Offset(22, 24, "ORGANIZATION"), Offset(120, 133, "LAWYER")]
    assert normalize_offsets(data1) == [Offset(5, 10, "LAWYER"), Offset(18, 24, "ORGANIZATION"), Offset(120, 133, "LAWYER")]
    data2 = [Offset(71, 75, "PERS"), Offset(76, 85, "PERS")]
    assert normalize_offsets(data2) == [Offset(71, 85, "PERS")]
    data3 = [Offset(5, 10, "LAWYER"), Offset(71, 75, "PERS"), Offset(76, 85, "PERS"), Offset(120, 133, "LAWYER")]
    assert normalize_offsets(data3) == [Offset(5, 10, "LAWYER"), Offset(71, 85, "PERS"), Offset(120, 133, "LAWYER")]
    data4 = [Offset(5, 10, "LAWYER"), Offset(77, 85, "PERS"), Offset(77, 85, "PERS"), Offset(120, 133, "LAWYER")]
    assert normalize_offsets(data4) == [Offset(5, 10, "LAWYER"), Offset(77, 85, "PERS"), Offset(120, 133, "LAWYER")]
    data5 = [Offset(16, 20, "PERS"), Offset(21, 30, "PERS")]
    assert normalize_offsets(data5) == [Offset(16, 30, "PERS")]
    data6 = [Offset(10, 21, "PERS"), Offset(22, 30, "PERS")]
    assert normalize_offsets(data6) == [Offset(10, 30, "PERS")]
    data7 = []
    assert normalize_offsets(data7) == []
    data8 = [Offset(1, 1, "PERS")]
    assert normalize_offsets(data8) == []
    data9 = [Offset(1, 3, "PERS")]
    assert normalize_offsets(data9, min_offset_size=2) == []
    data10 = [Offset(1, 10, "PERS"), Offset(1, 10, "PERS"), Offset(3, 10, "PERS")]
    assert normalize_offsets(data10) == [Offset(1, 10, "PERS")]
    data11 = [Offset(0, 34, "ORGANIZATION"), Offset(0, 8, "ORGANIZATION")]
    assert normalize_offsets(data11) == [Offset(0, 34, "ORGANIZATION")]
    data14 = [Offset(21, 33, "DATE"), Offset(35, 55, "PERS")]
    assert normalize_offsets(data14) == data14
    data15 = [Offset(start=21, end=37, type='DATE'), Offset(start=45, end=47, type='ORGANIZATION')]
    assert normalize_offsets(data15, min_offset_size=2) == [Offset(21, 37, "DATE")]
    data16 = [Offset(1, 3, "PERS")]
    assert normalize_offsets(data9) == data16
    data17 = [Offset(1, 5, "PERS"), Offset(6, 10, "PERS")]
    assert normalize_offsets(data17) == [Offset(1, 10, "PERS")]
    data18 = [Offset(1, 5, "PERS"), Offset(6, 10, "ORGANIZATION")]
    assert normalize_offsets(data18) == data18
    data19 = [Offset(1, 5, "PERS"), Offset(7, 10, "ORGANIZATION")]
    assert normalize_offsets(data19) == data19
