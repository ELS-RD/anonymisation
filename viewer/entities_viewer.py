from spacy import displacy

import warnings

from generate_trainset.extract_node_values import get_paragraph_from_file
from ner.model_factory import get_empty_model
from resources.config_provider import get_config_default

warnings.filterwarnings('ignore')

config_training = get_config_default()
model_dir_path = config_training["model_dir_path"]
xml_dev_path = config_training["xml_dev_path"]
nlp = get_empty_model(load_labels_for_training=False)
nlp = nlp.from_disk(model_dir_path)

DEV_DATA = get_paragraph_from_file(xml_dev_path,
                                   keep_paragraph_without_annotation=True)
docs = list()
for (case_id, text, _, _) in DEV_DATA[0:10]:
    doc = nlp(text)
    # doc.user_data['title'] = case_id
    docs.append(doc)

# https://spacy.io/usage/linguistic-features#section-named-entities
# check is None
docs[10].char_span(0, 10, label='PRESIDENT')


colors = {'PARTIE_PP': '#ff9933',
          'ADRESSE': '#ff99cc',
          'PARTIE_PM': '#00ccff',
          'AVOCAT': '#ccffcc',
          'MAGISTRAT': '#ccccff',
          'GREFFIER': '#ccccff'}
options = {'ents': None, 'colors': colors}
displacy.serve(docs, style='ent', minify=True, port=5000, options=options)
