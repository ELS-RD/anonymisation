import spacy

from resources.config_provider import get_config_default
from xml_parser.extract_node_value import get_paragraph_from_file


config_training = get_config_default()
model_dir_path = config_training["model_dir_path"]
xml_test_path = config_training["xml_test_path"]

nlp = spacy.load(model_dir_path)

TEST_DATA = get_paragraph_from_file(xml_test_path, spacy_format=False)

for texts, extracted_text, annotations in TEST_DATA:
    doc = nlp(texts)
    entities_spacy = set([ent.text for ent in doc.ents])
    if entities_spacy != set(extracted_text):
        print(extracted_text)
        print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
        print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])
