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

from xml_extractions.common_xml_parser_function import read_xml


def parse_xml_header(path: str):
    """
    Extract some values from Jurica XML headers
    :param path: path to the Jurica XML file
    :return: a dict, 1 slot per legal case, for each slot, there is a dict of list with values
    """
    tree = read_xml(path)
    nodes = tree.xpath('//Juri|//MetaJuri//DecisionTraitee/Numero|//Demandeurs//Texte|//Demandeurs//TexteAnonymise|'
                       '//MetaJuri/Defendeurs//TexteAnonymise|//MetaJuri/Defendeurs//Texte|'
                       '//Greffier|//Avocat|//DecisionTraitee/Date')

    headers_content = dict()

    for node in nodes:
        if node.tag == "Juri":
            # init empty mutable list
            # in following steps, these lists will be updated
            current_case = dict()
            defendeur_full = list()
            defendeur_hidden = list()
            demandeur_full = list()
            demandeur_hidden = list()
            greffier = list()
            avocat = list()
            conseiller = list()
            president = list()
            # need to be a mutable list to get the update
            # in Python str are immutable, so future update would be impossible
            numero = list()
            date = list()

            current_case['defendeur_fullname'] = defendeur_full
            current_case['defendeur_hidden'] = defendeur_hidden
            current_case['demandeur_fullname'] = demandeur_full
            current_case['demandeur_hidden'] = demandeur_hidden
            current_case['avocat'] = avocat
            current_case['president'] = president
            current_case['conseiller'] = conseiller
            current_case['greffier'] = greffier
            current_case['numero'] = numero
            current_case['date'] = date

            headers_content[node.get("id")] = current_case

        if node.tag == "Numero":
            numero.append(node.text)
        if node.tag == "Date":
            date.append(node.text)
        if "Defendeurs" in tree.getpath(node):
            if node.tag == "Texte":
                defendeur_full.append(node.text)
            if node.tag == "TexteAnonymise":
                defendeur_hidden.append(node.text)
        if "Demandeurs" in tree.getpath(node):
            if node.tag == "Texte":
                demandeur_full.append(node.text)
            if node.tag == "TexteAnonymise":
                demandeur_hidden.append(node.text)
        if node.tag == "Greffier":
            greffier.append(node.text)
        if node.tag == "Avocat":
            avocat.append(node.text)
        if node.tag == "President":
            president.append(node.text)
        if node.tag == "Conseiller":
            conseiller.append(node.text)

    return headers_content


def parse_xml_headers(folder_path: str) -> dict:
    """
    Extract some values from all files from a provided folder using :func:`parse_xml_header`.
    :param folder_path: path where the XML files are stored
    :return: a dict, 1 slot per legal case, for each slot, there is a dict of list with values
    """
    all_headers = dict()
    paths = os.listdir(folder_path)
    assert len(paths) > 0
    for path in paths:
        if path.endswith(".xml"):
            current_path = os.path.join(folder_path, path)
            current_header = parse_xml_header(current_path)
            all_headers.update(current_header)

    return all_headers
