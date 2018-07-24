import pickle

from tqdm import tqdm

from generate_trainset.build_dict_from_recognized_entities import get_frequent_entities, get_frequent_entities_matcher, \
    get_frequent_entities_matches
from generate_trainset.court_matcher import CourtName
from generate_trainset.extend_names import ExtendNames
from generate_trainset.extract_header_values import parse_xml_headers
from generate_trainset.extract_node_values import get_paragraph_from_folder
from generate_trainset.match_header import MatchValuesFromHeaders
from generate_trainset.match_patterns import get_company_names, get_judge_name, get_clerk_name, get_lawyer_name, \
    get_addresses, get_partie_pp, \
    get_all_name_variation, find_address_in_block_of_paragraphs, \
    get_juridictions
from generate_trainset.modify_strings import random_case_change, remove_key_words
from generate_trainset.normalize_offset import normalize_offsets, remove_offset_space, clean_offsets_from_unwanted_words
from generate_trainset.postal_code_dictionary_matcher import PostalCodeCity
from ner.training_function import train_model
from resources.config_provider import get_config_default
from viewer.spacy_viewer import convert_offsets_to_spacy_docs, view_spacy_docs

config_training = get_config_default()
xml_train_path = config_training["xml_train_path"]
model_dir_path = config_training["model_dir_path"]
n_iter = int(config_training["number_iterations"])
batch_size = int(config_training["batch_size"])
dropout_rate = float(config_training["dropout_rate"])
training_set_export_path = config_training["training_set"]
train_dataset = False  # bool(config_training["train_data_set"])
export_dataset = False  # not bool(config_training["train_data_set"])

TRAIN_DATA = get_paragraph_from_folder(folder_path=xml_train_path,
                                       keep_paragraph_without_annotation=True)
TRAIN_DATA = list(TRAIN_DATA)[0:100000]
case_header_content = parse_xml_headers(folder_path=xml_train_path)

current_case_paragraphs = list()
current_case_offsets = list()
previous_case_id = None
current_item_header = None
headers_matcher = None

postal_code_city_matcher = PostalCodeCity()
court_names_matcher = CourtName()
doc_annotated = list()
last_document_offsets = list()
last_document_texts = list()

if export_dataset:
    frequent_entities_dict = dict()
else:
    # Disable this part to generate a new set of entities
    frequent_entities_dict = get_frequent_entities(path_trainset=training_set_export_path,
                                                   threshold_occurrences=100)

frequent_entities_matcher = get_frequent_entities_matcher(content=frequent_entities_dict)

with tqdm(total=len(case_header_content)) as progress_bar:
    for current_case_id, xml_paragraph, xml_extracted_text, xml_offset in TRAIN_DATA:
        # when we change of legal case, apply matcher to each paragraph of the previous case
        if current_case_id != previous_case_id:
            if len(current_case_paragraphs) > 0:
                current_doc_extend_pp_name_pattern = ExtendNames(texts=current_case_paragraphs,
                                                                 offsets=current_case_offsets,
                                                                 type_name="PARTIE_PP")

                # current_doc_extend_pm_name_pattern = ExtendNames(texts=current_case_paragraphs,
                #                                                  offsets=current_case_offsets,
                #                                                  type_name="PARTIE_PM")
                #
                # current_doc_extend_lawyer_name_pattern = ExtendNames(texts=current_case_paragraphs,
                #                                                      offsets=current_case_offsets,
                #                                                      type_name="AVOCAT")
                #
                # current_doc_extend_judge_name_pattern = ExtendNames(texts=current_case_paragraphs,
                #                                                     offsets=current_case_offsets,
                #                                                     type_name="MAGISTRAT")

                for current_paragraph, current_xml_offset in zip(current_case_paragraphs, current_case_offsets):

                    # if "ACM IARD - ASSURANCE CREDIT MUTUEL".lower() in current_paragraph.lower():
                    #     raise Exception("STOP")

                    match_from_headers = headers_matcher.get_matched_entities(current_paragraph)

                    company_names_offset = get_company_names(current_paragraph)
                    full_name_pp = current_doc_extend_pp_name_pattern.get_extended_names(text=current_paragraph)
                    partie_pp = get_partie_pp(current_paragraph)
                    judge_names = get_judge_name(current_paragraph)
                    clerk_names = get_clerk_name(current_paragraph)
                    lawyer_names = get_lawyer_name(current_paragraph)
                    addresses = get_addresses(current_paragraph)
                    court_name = get_juridictions(current_paragraph)
                    postal_code_matches = postal_code_city_matcher.get_matches(text=current_paragraph)
                    court_names_matches = court_names_matcher.get_matches(text=current_paragraph)
                    frequent_entities = get_frequent_entities_matches(matcher=frequent_entities_matcher,
                                                                      frequent_entities_dict=frequent_entities_dict,
                                                                      text=current_paragraph)

                    all_matches = (match_from_headers +
                                   current_xml_offset +
                                   company_names_offset +
                                   full_name_pp +
                                   judge_names +
                                   clerk_names +
                                   lawyer_names +
                                   partie_pp +
                                   postal_code_matches +
                                   frequent_entities +
                                   court_name +
                                   court_names_matches +
                                   addresses)

                    if len(all_matches) > 0:

                        normalized_offsets = normalize_offsets(all_matches)
                        last_document_texts.append(current_paragraph)
                        last_document_offsets.append(normalized_offsets)

                    elif current_paragraph.isupper() and len(current_paragraph) > 10:
                        # add empty title paragraph to avoid fake solution
                        last_document_texts.append(current_paragraph)
                        last_document_offsets.append([])

            last_document_offsets = find_address_in_block_of_paragraphs(texts=last_document_texts,
                                                                        offsets=last_document_offsets)

            if len(last_document_offsets) > 0:
                last_doc_offset_with_var = get_all_name_variation(texts=last_document_texts,
                                                                  offsets=last_document_offsets,
                                                                  threshold_span_size=4)

                last_doc_with_extended_offsets = ExtendNames.get_extended_extracted_name_multiple_texts(
                    texts=last_document_texts,
                    offsets=last_doc_offset_with_var,
                    type_name="PARTIE_PP")

                last_doc_with_extended_offsets = ExtendNames.get_extended_extracted_name_multiple_texts(
                    texts=last_document_texts,
                    offsets=last_doc_with_extended_offsets,
                    type_name="PARTIE_PM")

                last_doc_with_extended_offsets = ExtendNames.get_extended_extracted_name_multiple_texts(
                    texts=last_document_texts,
                    offsets=last_doc_with_extended_offsets,
                    type_name="AVOCAT")

                last_doc_with_extended_offsets = ExtendNames.get_extended_extracted_name_multiple_texts(
                    texts=last_document_texts,
                    offsets=last_doc_with_extended_offsets,
                    type_name="MAGISTRAT")

                last_doc_with_ext_offset_and_var = get_all_name_variation(texts=last_document_texts,
                                                                          offsets=last_doc_with_extended_offsets,
                                                                          threshold_span_size=4)

                last_doc_offset_unwanted_words_removed = [clean_offsets_from_unwanted_words(text, off) for text, off in
                                                          zip(last_document_texts,
                                                              last_doc_with_ext_offset_and_var)]

                last_doc_offsets_no_space = [remove_offset_space(text, off) for text, off in
                                             zip(last_document_texts,
                                                 last_doc_offset_unwanted_words_removed)]

                last_doc_offsets_normalized = [normalize_offsets(off) for off in last_doc_offsets_no_space]

                last_doc_remove_keywords = [remove_key_words(text=text,
                                                             offsets=off,
                                                             rate=20) for text, off in
                                            zip(last_document_texts,
                                                last_doc_offsets_normalized)]

                last_doc_remove_keywords_text, last_doc_remove_keywords_offsets = zip(*last_doc_remove_keywords)

                last_doc_txt_case_updated = [random_case_change(text=text,
                                                                offsets=off,
                                                                rate=20) for text, off in
                                             zip(last_doc_remove_keywords_text,
                                                 last_doc_remove_keywords_offsets)]

                last_doc_remove_keywords_offsets_norm = [normalize_offsets(off) for off in
                                                         last_doc_remove_keywords_offsets]

                # , "case_id": previous_case_id
                [doc_annotated.append((previous_case_id, txt, {'entities': off})) for txt, off in
                 zip(last_doc_txt_case_updated,
                     last_doc_remove_keywords_offsets_norm)]

                last_document_texts.clear()
                last_document_offsets.clear()

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

print("Number of tags:", sum([len(i[2]['entities']) for i in doc_annotated]))

if train_dataset:
    train_model(data=doc_annotated,
                folder_to_save_model=model_dir_path,
                n_iter=n_iter,
                batch_size=batch_size,
                dropout_rate=dropout_rate)

if export_dataset:
    with open(training_set_export_path, 'wb') as export_training_set_file:
        pickle.dump(obj=doc_annotated, file=export_training_set_file, protocol=pickle.HIGHEST_PROTOCOL)

# Display training set
docs = convert_offsets_to_spacy_docs(doc_annotated[0:10000], model_dir_path)
view_spacy_docs(docs)
