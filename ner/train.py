# coding: utf8

# https://github.com/explosion/spaCy/issues/1530


from tqdm import tqdm

from generate_trainset.extract_header_values import parse_xml_headers
from generate_trainset.extract_node_values import get_paragraph_from_folder
from generate_trainset.first_name_dictionary import get_first_name_matcher, get_matches
from generate_trainset.generate_names import get_company_names, random_case_change, \
    get_extend_extracted_name_pattern, get_extended_extracted_name, get_judge_name, get_clerk_name, get_lawyer_name, \
    get_addresses, get_list_of_partie_pm_from_headers_to_search, get_list_of_partie_pp_from_headers_to_search, \
    get_list_of_lawyers_from_headers_to_search, get_list_of_president_from_headers_to_search, \
    get_list_of_conseiller_from_headers_to_search, get_list_of_clerks_from_headers_to_search
from generate_trainset.normalize_offset import normalize_offsets
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
TRAIN_DATA = list(TRAIN_DATA)[0:100000]
case_header_content = parse_xml_headers(folder_path=xml_train_path)

current_case_paragraphs = list()
current_case_offsets = list()
previous_case_id = None
current_item_header = None

matcher_partie_pm = None
matcher_partie_pp = None
matcher_avocat = None
matcher_president = None
matcher_conseiller = None
matcher_greffier = None

first_name_matcher = get_first_name_matcher()
doc_annotated = list()
# TODO to delete when ready
no_offset_sentences_with_risk = list()

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
                    match_from_headers += get_matches(matcher_avocat, current_paragraph, "AVOCAT")
                    match_from_headers += get_matches(matcher_avocat, current_paragraph, "CONSEILLER")
                    match_from_headers += get_matches(matcher_president, current_paragraph, "PRESIDENT")
                    match_from_headers += get_matches(matcher_greffier, current_paragraph, "GREFFIER")

                    company_names_offset = get_company_names(current_paragraph)
                    full_name_pp = get_extended_extracted_name(text=current_paragraph,
                                                               pattern=current_doc_extend_name_pattern,
                                                               type_name="PARTIE_PP")
                    judge_names = get_judge_name(current_paragraph)
                    clerk_names = get_clerk_name(current_paragraph)
                    lawyer_names = get_lawyer_name(current_paragraph)
                    # TODO to reactivate when ready
                    # first_name_matches = get_first_name_matches(first_name_matcher, current_paragraph)
                    addresses = get_addresses(current_paragraph)

                    all_matches = (match_from_headers +
                                   current_xml_offset +
                                   company_names_offset +
                                   full_name_pp +
                                   judge_names +
                                   clerk_names +
                                   lawyer_names +
                                   addresses)

                    # if (len(first_name_matches) > 0) and (len(all_matches) == 0):
                    #     print(current_paragraph)

                    if len(all_matches) > 0:

                        normalized_offsets = normalize_offsets(all_matches)
                        current_paragraph_case_updated = random_case_change(text=current_paragraph,
                                                                            offsets=normalized_offsets,
                                                                            rate=5)
                        doc_annotated.append((current_paragraph_case_updated,
                                              {'entities': normalized_offsets}))

                    elif current_paragraph.isupper() and len(current_paragraph) > 10:
                        # add empty title paragraph to avoid fake solution
                        doc_annotated.append((current_paragraph, {'entities': []}))

                    # TODO to delete when ready
                    risk_keywords = ["Monsieur", "Madame", "M ", "Mme ", "M. "]
                    if any(keyword in current_paragraph for keyword in risk_keywords) and len(all_matches) == 0:
                        no_offset_sentences_with_risk.append(current_paragraph)

            # update when one case is finished
            progress_bar.update()

            # init element specific to the current legal case
            current_case_paragraphs.clear()
            current_case_offsets.clear()
            previous_case_id = current_case_id
            current_item_header = case_header_content[current_case_id]

            matcher_partie_pm = get_list_of_partie_pm_from_headers_to_search(current_item_header)
            matcher_partie_pp = get_list_of_partie_pp_from_headers_to_search(current_item_header)
            matcher_avocat = get_list_of_lawyers_from_headers_to_search(current_item_header)
            matcher_president = get_list_of_president_from_headers_to_search(current_item_header)
            matcher_conseiller = get_list_of_conseiller_from_headers_to_search(current_item_header)
            matcher_greffier = get_list_of_clerks_from_headers_to_search(current_item_header)

        current_case_paragraphs.append(xml_paragraph)
        current_case_offsets.append(xml_offset)

for risk_sentence in no_offset_sentences_with_risk:
    print(risk_sentence)

for text, annot in doc_annotated:
    if len(annot['entities']) > 0:
        for start, end, type_name in annot['entities']:
            print(start, end, "|", text[start:end], "|", type_name)

train_model(data=doc_annotated,
            folder_to_save_model=model_dir_path,
            n_iter=n_iter,
            batch_size=batch_size,
            dropout_rate=dropout_rate)
