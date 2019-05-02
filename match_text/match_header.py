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

from match_text_unsafe.match_acora import AcoraMatcher


class MatchValuesFromHeaders:
    matcher_partie_pm = None
    matcher_partie_pp = None
    matcher_lawyers = None
    matcher_president = None
    matcher_conseiller = None
    matcher_clerks = None
    current_header = dict()
    threshold_size = 0

    def __init__(self, current_header: dict, threshold_size: int):
        """
        Build a matcher of values from headers
        :param current_header: : original dict build from values from headers
        :param threshold_size: minimum size of a word to be added to a matcher
        """
        self.current_header = current_header
        self.threshold_size = threshold_size

        self.matcher_partie_pm = self.get_matcher_of_partie_pm_from_headers()
        self.matcher_partie_pp = self.get_matcher_of_partie_pp_from_headers()
        self.matcher_lawyers = self.get_matcher_of_lawyers_from_headers()
        self.matcher_president = self.get_matcher_of_president_from_headers()
        self.matcher_conseiller = self.get_matcher_of_conseiller_from_headers()
        self.matcher_clerks = self.get_matcher_of_clerks_from_headers()

    def get_matched_entities(self, current_paragraph: str) -> list:
        current_doc_offsets = self.matcher_partie_pp.get_matches(text=current_paragraph, tag="PERS")
        current_doc_offsets += self.matcher_partie_pm.get_matches(text=current_paragraph, tag="ORGANIZATION")
        current_doc_offsets += self.matcher_lawyers.get_matches(text=current_paragraph, tag="LAWYER")
        current_doc_offsets += self.matcher_president.get_matches(text=current_paragraph, tag="JUDGE_CLERK")
        current_doc_offsets += self.matcher_clerks.get_matches(text=current_paragraph, tag="JUDGE_CLERK")

        return current_doc_offsets

    def get_matcher_of_partie_pp_from_headers(self) -> AcoraMatcher:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        # this way of init assure that the matcher doesn't expect binary data
        # this may happen if we load empty arrays through update function for instance
        span_text = list()
        for full_content, short_content in zip(
                self.current_header['defendeur_fullname'] + self.current_header['demandeur_fullname'],
                self.current_header['defendeur_hidden'] + self.current_header['demandeur_hidden']):
            if short_content is not None:
                span_text.append(full_content)
                # first_name, last_name = get_first_last_name(full_content)
                # if len(first_name) > self.threshold_size:
                #     matcher.add(first_name)
                # if len(last_name) > self.threshold_size:
                #     matcher.add(last_name)

        matcher = AcoraMatcher(content=span_text, ignore_case=False)
        return matcher

    def get_matcher_of_partie_pm_from_headers(self) -> AcoraMatcher:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        span_text = list()

        for full_content, short_content in zip(
                self.current_header['defendeur_fullname'] + self.current_header['demandeur_fullname'],
                self.current_header['defendeur_hidden'] + self.current_header['demandeur_hidden']):
            if short_content is None:
                span_text.append(full_content)

        matcher = AcoraMatcher(content=span_text, ignore_case=False)
        return matcher

    def get_matcher_of_lawyers_from_headers(self) -> AcoraMatcher:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        header_content = self.current_header['avocat']
        matcher = AcoraMatcher(content=header_content, ignore_case=False)

        # for content in header_content:
        #     first_name, last_name = get_first_last_name(content)
        #     if len(first_name) > self.threshold_size:
        #         matcher.add(first_name)
        #     if len(last_name) > self.threshold_size:
        #         matcher.add(last_name)
        return matcher

    def get_matcher_of_president_from_headers(self) -> AcoraMatcher:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        header_content = self.current_header['president']
        matcher = AcoraMatcher(content=header_content, ignore_case=False)
        # for content in header_content:
        #     first_name, last_name = get_first_last_name(content)
        #     if len(first_name) > self.threshold_size:
        #         matcher.add(first_name)
        #     if len(last_name) > self.threshold_size:
        #         matcher.add(last_name)
        return matcher

    def get_matcher_of_conseiller_from_headers(self) -> AcoraMatcher:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        header_content = self.current_header['conseiller']
        matcher = AcoraMatcher(content=header_content, ignore_case=False)
        # for content in header_content:
        #     first_name, last_name = get_first_last_name(content)
        #     if len(first_name) > self.threshold_size:
        #         matcher.add(first_name)
        #     if len(last_name) > self.threshold_size:
        #         matcher.add(last_name)
        return matcher

    def get_matcher_of_clerks_from_headers(self) -> AcoraMatcher:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        header_content = self.current_header['greffier']
        matcher = AcoraMatcher(content=header_content, ignore_case=False)
        # for content in header_content:
        #     first_name, last_name = get_first_last_name(content)
        #     if len(first_name) > self.threshold_size:
        #         matcher.add(first_name)
        #     if len(last_name) > self.threshold_size:
        #         matcher.add(last_name)
        return matcher
