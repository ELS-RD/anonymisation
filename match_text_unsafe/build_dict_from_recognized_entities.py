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

import pickle
import warnings

from match_text_unsafe.match_acora import AcoraMatcher
from ner.model_factory import entity_types
from resources.config_provider import get_config_default

config_training = get_config_default()
training_set_export_path = config_training["training_set"]


class FrequentEntities(object):
    matcher = None
    frequent_entities_dict = None

    def __init__(self, path_trainset: str, threshold_occurrences: int, type_name_to_not_load: list, load_data: bool):
        """
        Build an Acora matcher based on the dict of frequent entities
        :param path_trainset: path to a file storing the entity
        :param threshold_occurrences: minimum number of occurences of the entity
        :param type_name_to_not_load: type of entities that should not be loaded to avoid fake match
        :param load_data: boolean to decide if data should be loaded or not
        :return: an Acora matcher matcher
        """
        if load_data:
            self.frequent_entities_dict = self.__read_frequent_entities(path_trainset=path_trainset,
                                                                        threshold_occurrences=threshold_occurrences,
                                                                        type_name_to_not_load=type_name_to_not_load)
            self.matcher = AcoraMatcher(content=list(self.frequent_entities_dict.keys()),
                                        ignore_case=True)
        else:
            self.matcher = AcoraMatcher(content=["!@#$%^&*()"],
                                        ignore_case=True)

    @classmethod
    def test_builder(cls, content: dict):
        """
        Build an instance of this object for tests.
        In particular, don't try to read saved data
        :param content: a dictionary of entities to load
        :return: an instance of FrequentEntities class
        """
        instance = FrequentEntities(path_trainset="",
                                    threshold_occurrences=0,
                                    load_data=False,
                                    type_name_to_not_load=[])
        instance.frequent_entities_dict = content
        instance.matcher = AcoraMatcher(content=list(content.keys()),
                                        ignore_case=True)
        return instance

    @staticmethod
    def __read_frequent_entities(path_trainset: str, threshold_occurrences: int, type_name_to_not_load: list) -> dict:
        """
        Analyze recognized entities and return those over a defined threshold in a dict entity -> type_name
        """
        try:
            with open(path_trainset, 'rb') as f:
                data = pickle.load(file=f)

            def get_default_dict_value() -> dict:
                default_dict_value = dict([(token, set()) for token in entity_types])
                # default_dict_value['general_count'] = 0
                return default_dict_value

            exhaustive_dict = dict()

            for case_id, text, entities in data:
                for start_offset, end_offset, type_name in entities:
                    entity_span = text[start_offset:end_offset].lower()
                    current_count = exhaustive_dict.get(entity_span, get_default_dict_value())
                    current_count[type_name].add(case_id)
                    exhaustive_dict[entity_span] = current_count

            final_list = list()

            for entity_span, dict_counts in exhaustive_dict.items():

                max_count = 0
                max_type_name = None
                for type_name, case_ids in dict_counts.items():
                    current_count = len(case_ids)
                    if current_count > max_count:
                        max_type_name = type_name
                        max_count = current_count

                if (max_count > threshold_occurrences) and \
                        (len(entity_span) > 3) \
                        and (max_type_name not in type_name_to_not_load):
                    final_list.append((entity_span, max_type_name))

            return dict(final_list)

        except:
            warnings.warn("Empty dict of frequent entities", Warning)
            return dict()

    def get_matches(self, text: str) -> list:
        """
        Find matches of frequent entities in the provided text
        :param text: original text
        :return: a list of offsets
        """
        match_results = self.matcher.findall(text)
        entities = list()
        for match_text, start_offset in match_results:
            end_offset = start_offset + len(match_text)
            entity_span = text[start_offset:end_offset]

            # end_offset is one character after the end of the selection,
            # so it can be equal to the last charcter offset of the text + 1
            last_char_ok = (end_offset == len(text)) or (not text[end_offset].isalnum())

            first_char_ok = (start_offset == 0 or not text[start_offset - 1].isalnum()) and \
                            (text[start_offset].isupper() or text[start_offset].isdecimal())

            if first_char_ok and last_char_ok:
                type_name = self.frequent_entities_dict[entity_span.lower()]
                entities.append((start_offset, end_offset, type_name))

        return entities
