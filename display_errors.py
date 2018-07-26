from generate_trainset.extract_node_values import get_paragraph_from_file
from ner.model_factory import get_empty_model
from resources.config_provider import get_config_default

config_training = get_config_default()
model_dir_path = config_training["model_dir_path"]
xml_dev_path = config_training["xml_dev_path"]
nlp = get_empty_model(load_labels_for_training=False)
nlp = nlp.from_disk(model_dir_path)

DEV_DATA = get_paragraph_from_file(xml_dev_path,
                                   keep_paragraph_without_annotation=True)

for case_id, texts, xml_extracted_text, annotations in DEV_DATA:
    doc = nlp(texts)

    spacy_extracted_text_ad_pp = [ent.text for ent in doc.ents if ent.label_ in ["ADRESSE", "PARTIE_PP"]]

    spacy_extracted_text = [ent.text for ent in doc.ents]
    str_rep_spacy = ' '.join(spacy_extracted_text)
    match = [span_xml in str_rep_spacy for span_xml in xml_extracted_text]

    if sum(match) < len(xml_extracted_text):
        print("XML")
        print('Entities X', xml_extracted_text)
        print('Entities S', [(ent.text, ent.label_) for ent in doc.ents])
        print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])
    elif len(xml_extracted_text) < len(spacy_extracted_text_ad_pp):
        print("SPACY")
        print('Entities X', xml_extracted_text)
        print('Entities S', [(ent.text, ent.label_) for ent in doc.ents])
        print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])
