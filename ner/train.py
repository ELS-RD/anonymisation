# coding: utf8

# https://github.com/explosion/spaCy/issues/1530


from tqdm import tqdm

from generate_trainset.extract_header_values import parse_xml_headers
from generate_trainset.extract_node_values import get_paragraph_from_folder
from generate_trainset.first_name_dictionary import get_first_name_matcher, get_first_name_matches
from generate_trainset.match_acora import get_matches
from generate_trainset.match_patterns import get_company_names, get_extend_extracted_name_pattern, \
    get_extended_extracted_name, get_judge_name, get_clerk_name, get_lawyer_name, \
    get_addresses, get_matcher_of_partie_pm_from_headers, get_matcher_of_partie_pp_from_headers, \
    get_matcher_of_lawyers_from_headers, get_matcher_of_president_from_headers, \
    get_matcher_of_conseiller_from_headers, get_matcher_of_clerks_from_headers, get_partie_pp, \
    get_all_name_variation, get_extended_extracted_name_multiple_texts
from generate_trainset.modify_strings import random_case_change, remove_key_words
from generate_trainset.normalize_offset import normalize_offsets, remove_offset_space, clean_offsets_from_unwanted_words
from ner.training_function import train_model
from resources.config_provider import get_config_default

config_training = get_config_default()
xml_train_path = config_training["xml_train_path"]
model_dir_path = config_training["model_dir_path"]
n_iter = int(config_training["number_iterations"])
batch_size = int(config_training["batch_size"])
dropout_rate = float(config_training["dropout_rate"])

TRAIN_DATA = get_paragraph_from_folder(folder_path=xml_train_path,
                                       keep_paragraph_without_annotation=True)
TRAIN_DATA = list(TRAIN_DATA)  # [0:100000]
case_header_content = parse_xml_headers(folder_path=xml_train_path)

current_case_paragraphs = list()
current_case_offsets = list()
previous_case_id = None
current_item_header = None

matcher_partie_pm = None
matcher_partie_pp = None
matcher_lawyers = None
matcher_president = None
matcher_conseiller = None
matcher_clerks = None

first_name_matcher = get_first_name_matcher()
doc_annotated = list()
last_document_offsets = list()
last_document_texts = list()
# TODO to delete when ready
to_delete_no_offset_sentences_with_risk = list()

with tqdm(total=len(case_header_content)) as progress_bar:
    for current_case_id, xml_paragraph, xml_extracted_text, xml_offset in TRAIN_DATA:
        # when we change of legal case, apply matcher to each paragraph of the previous case
        if current_case_id != previous_case_id:
            if len(current_case_paragraphs) > 0:
                current_doc_extend_name_pattern = get_extend_extracted_name_pattern(texts=current_case_paragraphs,
                                                                                    offsets=current_case_offsets,
                                                                                    type_name_to_keep="PARTIE_PP")

                for current_paragraph, current_xml_offset in zip(current_case_paragraphs, current_case_offsets):
                    match_from_headers = get_matches(matcher_partie_pp, current_paragraph, "PARTIE_PP")
                    match_from_headers += get_matches(matcher_partie_pm, current_paragraph, "PARTIE_PM")
                    match_from_headers += get_matches(matcher_lawyers, current_paragraph, "AVOCAT")
                    match_from_headers += get_matches(matcher_lawyers, current_paragraph, "CONSEILLER")
                    match_from_headers += get_matches(matcher_president, current_paragraph, "PRESIDENT")
                    match_from_headers += get_matches(matcher_clerks, current_paragraph, "GREFFIER")

                    company_names_offset = get_company_names(current_paragraph)
                    full_name_pp = get_extended_extracted_name(text=current_paragraph,
                                                               pattern=current_doc_extend_name_pattern,
                                                               type_name="PARTIE_PP")
                    judge_names = get_judge_name(current_paragraph)
                    clerk_names = get_clerk_name(current_paragraph)
                    lawyer_names = get_lawyer_name(current_paragraph)

                    first_name_matches = get_first_name_matches(first_name_matcher, current_paragraph)
                    addresses = get_addresses(current_paragraph)
                    partie_pp = get_partie_pp(current_paragraph)

                    all_matches = (match_from_headers +
                                   current_xml_offset +
                                   company_names_offset +
                                   full_name_pp +
                                   judge_names +
                                   clerk_names +
                                   lawyer_names +
                                   partie_pp +
                                   first_name_matches +
                                   addresses)

                    if len(all_matches) > 0:

                        normalized_offsets = normalize_offsets(all_matches)
                        last_document_texts.append(current_paragraph)
                        last_document_offsets.append(normalized_offsets)

                    elif current_paragraph.isupper() and len(current_paragraph) > 10:
                        # add empty title paragraph to avoid fake solution
                        last_document_texts.append(current_paragraph)
                        last_document_offsets.append([])

                    risk_keywords = ["Monsieur", "Madame", " M ", "Mme ", "M. "]
                    if any(keyword in current_paragraph for keyword in risk_keywords) and len(all_matches) == 0:
                        to_delete_no_offset_sentences_with_risk.append(current_paragraph)

                    # if """L'altercation avec Alexandre et la violence des propos et du geste de la salariée est attestée par Alexandre PAUL""".lower() in current_paragraph.lower():
                    #     raise Exception("SSSSTOP")

            if len(last_document_offsets) > 0:
                last_doc_offset_with_var = get_all_name_variation(texts=last_document_texts,
                                                                  offsets=last_document_offsets,
                                                                  threshold_span_size=4)

                last_doc_with_extended_pp_offsets = get_extended_extracted_name_multiple_texts(
                    texts=last_document_texts,
                    offsets=last_doc_offset_with_var,
                    type_name="PARTIE_PP")

                last_doc_with_ext_offset_and_var = get_all_name_variation(texts=last_document_texts,
                                                                          offsets=last_doc_with_extended_pp_offsets,
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

                # , "case_id": previous_case_id
                [doc_annotated.append((txt, {'entities': off})) for txt, off in
                 zip(last_doc_txt_case_updated,
                     last_doc_remove_keywords_offsets)]

                last_document_texts.clear()
                last_document_offsets.clear()

            # update when one case is finished
            progress_bar.update()

            # init element specific to the current legal case
            current_case_paragraphs.clear()
            current_case_offsets.clear()
            previous_case_id = current_case_id
            current_item_header = case_header_content[current_case_id]

            matcher_partie_pm = get_matcher_of_partie_pm_from_headers(current_header=current_item_header)
            matcher_partie_pp = get_matcher_of_partie_pp_from_headers(current_header=current_item_header,
                                                                      threshold_size=3)
            matcher_lawyers = get_matcher_of_lawyers_from_headers(current_header=current_item_header,
                                                                  threshold_size=3)
            matcher_president = get_matcher_of_president_from_headers(current_header=current_item_header,
                                                                      threshold_size=3)
            matcher_conseiller = get_matcher_of_conseiller_from_headers(current_header=current_item_header,
                                                                        threshold_size=3)
            matcher_clerks = get_matcher_of_clerks_from_headers(current_header=current_item_header,
                                                                threshold_size=3)

        current_case_paragraphs.append(xml_paragraph)
        current_case_offsets.append(xml_offset)

for risk_sentence in to_delete_no_offset_sentences_with_risk:
    print(risk_sentence)

for text, tags in doc_annotated:
    if len(tags['entities']) > 0:
        for start, end, type_name in tags['entities']:
            # if "Madame".lower() in text[start:end].lower():
            print(start, end, text[start:end], type_name, text, sep="|")

print("Number of tags:", sum([len(i[1]['entities']) for i in doc_annotated]))

train_model(data=doc_annotated,
            folder_to_save_model=model_dir_path,
            n_iter=n_iter,
            batch_size=batch_size,
            dropout_rate=dropout_rate)
