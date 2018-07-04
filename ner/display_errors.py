import spacy
import configparser
from xml_parser.xml_parser import get_paragraph

config = configparser.ConfigParser()
config.read('resources/config.ini')
config_training = config['training']
model_dir_path = config_training["model_dir_path"]
xml_test_path = config_training["xml_test_path"]

nlp = spacy.load(model_dir_path)

TEST_DATA = get_paragraph(xml_test_path, spacy_format=False)

for texts, extracted_text, annotations in TEST_DATA:
    doc = nlp(texts)
    entities_spacy = [ent.text for ent in doc.ents]
    if entities_spacy != extracted_text:
        print(extracted_text)
        print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
        print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])
