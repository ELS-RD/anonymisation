import spacy

from resources.config_provider import get_config_default
from generate_trainset.extract_node_values import get_paragraph_from_file


config_training = get_config_default()
model_dir_path = config_training["model_dir_path"]
xml_dev_path = config_training["xml_dev_path"]

nlp = spacy.load(model_dir_path)

DEV_DATA = get_paragraph_from_file(xml_dev_path,
                                   keep_paragraph_without_annotation=True)

for case_id, texts, extracted_text, annotations in DEV_DATA:
    doc = nlp(texts)
    entities_spacy = set([ent.text for ent in doc.ents])
    if entities_spacy != set(extracted_text):
        print(extracted_text)
        print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
        print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])
    if len(entities_spacy) == 0 and any(word.isupper() and len(word) > 3 for word in texts.split()) and not texts.isupper():
        print("[EMPTY LINE]", texts)
