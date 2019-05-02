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
import sys
from random import seed

from tqdm import tqdm

from match_text.match_credit_card import get_credit_card_number
from match_text.match_licence_plate import get_licence_plate
from match_text.match_phone import get_phone_number
from match_text.match_social_security_number import get_social_security_number
from match_text_unsafe.build_dict_from_recognized_entities import FrequentEntities
from match_text_unsafe.find_header_values import parse_xml_headers
from match_text.match_address import get_addresses, find_address_in_block_of_paragraphs, clean_address_offsets
from match_text.match_bar import get_bar
from match_text.match_clerk import get_clerk_name
from match_text.match_courts import CourtName, get_juridictions
from match_text.match_date import get_date
from match_text_unsafe.extend_names import ExtendNames
from modify_text.change_case import random_case_change

from xml_extractions.extract_node_values import get_paragraph_from_folder
from match_text.match_doubtful_mwe import MatchDoubfulMwe
from match_text.match_extension_of_entity_name import get_all_name_variation
from match_text.match_header import MatchValuesFromHeaders
from match_text.match_judge import get_judge_name
from match_text.match_lawyer import get_lawyer_name
from match_text.match_natural_persons import get_partie_pers
from match_text.match_company_names import get_company_names
from match_text.match_rg import MatchRg, get_rg_from_regex
from modify_text.modify_strings import remove_key_words
from misc.normalize_offset import normalize_offsets, remove_spaces_included_in_offsets, \
    clean_offsets_from_unwanted_words
from match_text_unsafe.postal_code_dictionary_matcher import PostalCodeCity
from ner.training_function import train_model
from resources.config_provider import get_config_default
from viewer.spacy_viewer import convert_offsets_to_spacy_docs, view_spacy_docs

# reproducibility
seed(123)

config_training = get_config_default()
xml_train_path = config_training["xml_train_path"]
model_dir_path = config_training["model_dir_path"]
n_iter = int(config_training["number_iterations"])
batch_size = int(config_training["batch_size"])
dropout_rate = float(config_training["dropout_rate"])
training_set_export_path = config_training["training_set"]
change_case_rate = int(config_training["change_case_rate"])
remove_keyword_rate = int(config_training["remove_keyword_rate"])
frequent_entity_threshold = int(config_training["frequent_entity_threshold"])
number_of_paragraph_to_display = int(config_training["number_of_paragraph_to_display"])

assert len(sys.argv) <= 2

if len(sys.argv) == 2:
    param = sys.argv[1]
    train_dataset = "train_data_set" == param
    export_dataset = "export_dataset" == param
else:
    train_dataset = False
    export_dataset = False

TRAIN_DATA = get_paragraph_from_folder(folder_path=xml_train_path,
                                       keep_paragraph_without_annotation=True)
TRAIN_DATA = list(TRAIN_DATA)

if (not train_dataset) and (not export_dataset):
    print("Prepare training set for display")
    TRAIN_DATA = TRAIN_DATA[:number_of_paragraph_to_display]
elif train_dataset:
    print("Train model")
else:
    print("Save recurrent entities")

case_header_content = parse_xml_headers(folder_path=xml_train_path)

current_case_paragraphs = list()
current_case_offsets = list()
previous_case_id = None
current_item_header = None
headers_matcher = None
rg_matcher = None

postal_code_city_matcher = PostalCodeCity()
court_names_matcher = CourtName()
doubtful_mwe_matcher = MatchDoubfulMwe()
doc_annotated = list()

# TODO remove
# frequent_entities_matcher = FrequentEntities(path_trainset=training_set_export_path,
#                                              threshold_occurrences=frequent_entity_threshold,
#                                              load_data=not export_dataset,
#                                              type_name_to_not_load=["PERS", "UNKNOWN"])

with tqdm(total=len(case_header_content), unit=" paragraphs", desc="Generate NER dataset") as progress_bar:
    for current_case_id, xml_paragraph, xml_extracted_text, xml_offset in TRAIN_DATA:
        # when we change of legal case, apply matcher to each paragraph of the previous case
        if current_case_id != previous_case_id:
            last_document_offsets = list()
            last_document_texts = list()
            if len(current_case_paragraphs) > 0:
                current_doc_extend_pp_name_pattern = ExtendNames(texts=current_case_paragraphs,
                                                                 offsets=current_case_offsets,
                                                                 type_name="PERS")
                rg_matcher = MatchRg(case_id=previous_case_id)
                for current_paragraph, current_xml_offset in zip(current_case_paragraphs, current_case_offsets):

                    match_from_headers = headers_matcher.get_matched_entities(current_paragraph)

                    company_names_offset = get_company_names(current_paragraph)
                    full_name_pp = current_doc_extend_pp_name_pattern.get_extended_names(text=current_paragraph)
                    partie_pp = get_partie_pers(current_paragraph)
                    judge_names = get_judge_name(current_paragraph)
                    clerk_names = get_clerk_name(current_paragraph)
                    lawyer_names = get_lawyer_name(current_paragraph)
                    addresses = get_addresses(current_paragraph)
                    court_name = get_juridictions(current_paragraph)
                    case_dates = get_date(current_paragraph)
                    rg_from_regex = get_rg_from_regex(text=current_paragraph)
                    bar = get_bar(current_paragraph)
                    postal_code_matches = postal_code_city_matcher.get_matches(text=current_paragraph)
                    court_names_matches = court_names_matcher.get_matches(text=current_paragraph)
                    # frequent_entities = frequent_entities_matcher.get_matches(text=current_paragraph)
                    licence_plate_number = get_licence_plate(text=current_paragraph)
                    phone_numbers = get_phone_number(text=current_paragraph)

                    all_matches = (match_from_headers +
                                   current_xml_offset +
                                   company_names_offset +
                                   full_name_pp +
                                   judge_names +
                                   clerk_names +
                                   lawyer_names +
                                   partie_pp +
                                   postal_code_matches +
                                   # frequent_entities +
                                   court_name +
                                   court_names_matches +
                                   case_dates +
                                   bar +
                                   rg_from_regex +
                                   licence_plate_number +
                                   phone_numbers +
                                   addresses)

                    if len(all_matches) > 0:

                        normalized_offsets = normalize_offsets(all_matches)
                        last_document_texts.append(current_paragraph)
                        last_document_offsets.append(normalized_offsets)

                    elif current_paragraph.isupper() and len(current_paragraph) > 10:
                        # add empty title paragraph to avoid fake solution
                        last_document_texts.append(current_paragraph)
                        last_document_offsets.append([])

            assert len(last_document_texts) == len(last_document_offsets)

            last_document_offsets_with_addresses = find_address_in_block_of_paragraphs(texts=last_document_texts,
                                                                                       offsets=last_document_offsets)

            last_document_offsets_with_cleaned_addresses = clean_address_offsets(texts=last_document_texts,
                                                                                 offsets=last_document_offsets_with_addresses)

            if len(last_document_offsets_with_cleaned_addresses) > 0:
                last_doc_offset_with_rg = rg_matcher.get_rg_offset_from_texts(texts=last_document_texts,
                                                                              offsets=last_document_offsets_with_cleaned_addresses)

                last_doc_offset_with_var = get_all_name_variation(texts=last_document_texts,
                                                                  offsets=last_doc_offset_with_rg,
                                                                  threshold_span_size=4)

                last_doc_with_extended_offsets = ExtendNames.get_extended_extracted_name_multiple_texts(
                    texts=last_document_texts,
                    offsets=last_doc_offset_with_var,
                    type_name="PERS")

                last_doc_with_extended_offsets = ExtendNames.get_extended_extracted_name_multiple_texts(
                    texts=last_document_texts,
                    offsets=last_doc_with_extended_offsets,
                    type_name="ORGANIZATION")

                last_doc_with_extended_offsets = ExtendNames.get_extended_extracted_name_multiple_texts(
                    texts=last_document_texts,
                    offsets=last_doc_with_extended_offsets,
                    type_name="LAWYER")

                last_doc_with_extended_offsets = ExtendNames.get_extended_extracted_name_multiple_texts(
                    texts=last_document_texts,
                    offsets=last_doc_with_extended_offsets,
                    type_name="JUDGE_CLERK")

                last_doc_with_extended_offsets = ExtendNames.get_extended_extracted_name_multiple_texts(
                    texts=last_document_texts,
                    offsets=last_doc_with_extended_offsets,
                    type_name="JUDGE_CLERK")

                last_doc_with_ext_offset_and_var = get_all_name_variation(texts=last_document_texts,
                                                                          offsets=last_doc_with_extended_offsets,
                                                                          threshold_span_size=4)

                last_doc_offset_unwanted_words_rmved = [clean_offsets_from_unwanted_words(text, off) for text, off in
                                                        zip(last_document_texts,
                                                            last_doc_with_ext_offset_and_var)]

                last_doc_with_unknown_entities = doubtful_mwe_matcher. \
                    add_unknown_words_offsets(texts=last_document_texts,
                                              offsets=last_doc_offset_unwanted_words_rmved)

                last_doc_offsets_no_space = [remove_spaces_included_in_offsets(text, off) for text, off in
                                             zip(last_document_texts,
                                                 last_doc_with_unknown_entities)]

                last_doc_offsets_normalized = [normalize_offsets(off) for off in last_doc_offsets_no_space]

                last_doc_remove_keywords = [remove_key_words(text=text,
                                                             offsets=off,
                                                             rate=remove_keyword_rate) for text, off in
                                            zip(last_document_texts,
                                                last_doc_offsets_normalized)]

                last_doc_remove_keywords_text, last_doc_remove_keywords_offsets = zip(*last_doc_remove_keywords)

                last_doc_txt_case_updated = [random_case_change(text=text,
                                                                offsets=off,
                                                                rate=change_case_rate) for text, off in
                                             zip(last_doc_remove_keywords_text,
                                                 last_doc_remove_keywords_offsets)]

                last_doc_remove_keywords_offsets_norm = [normalize_offsets(off) for off in
                                                         last_doc_remove_keywords_offsets]

                [doc_annotated.append((previous_case_id, txt, off)) for txt, off in
                 zip(last_doc_txt_case_updated,
                     last_doc_remove_keywords_offsets_norm)]

            # update when one case is finished
            progress_bar.update()

            # init element specific to the current legal case
            current_case_paragraphs.clear()
            current_case_offsets.clear()
            previous_case_id = current_case_id
            current_item_header = case_header_content[current_case_id]

            headers_matcher = MatchValuesFromHeaders(current_header=current_item_header, threshold_size=3)

        current_case_paragraphs.append(xml_paragraph)
        current_case_offsets.append(xml_offset)

print("Number of tags:", sum([len(offsets) for _, _, offsets in doc_annotated]))

if train_dataset:
    train_model(data=doc_annotated,
                folder_to_save_model=model_dir_path,
                n_iter=n_iter,
                batch_size=batch_size,
                dropout_rate=dropout_rate)
elif export_dataset:
    with open(training_set_export_path, 'wb') as export_training_set_file:
        pickle.dump(obj=doc_annotated, file=export_training_set_file, protocol=pickle.HIGHEST_PROTOCOL)
else:
    # Display training set
    docs = convert_offsets_to_spacy_docs(doc_annotated)
    view_spacy_docs(docs, port=5000)
    print("view result on browser (localhost - port 5000)")
