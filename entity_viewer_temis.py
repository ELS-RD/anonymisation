from generate_trainset.extract_node_values import get_paragraph_from_file
from ner.model_factory import get_empty_model
from resources.config_provider import get_config_default
from viewer.spacy_viewer import view_spacy_docs

config_training = get_config_default()
model_dir_path = config_training["model_dir_path"]
xml_dev_path = config_training["xml_dev_path"]

DEV_DATA = get_paragraph_from_file(xml_dev_path,
                                   keep_paragraph_without_annotation=True)
DEV_DATA = list(DEV_DATA)[0:10000]

doc_annotated = list()

nlp = get_empty_model(load_labels_for_training=True)
nlp = nlp.from_disk(model_dir_path)

for current_case_id, xml_paragraph, xml_extracted_text, xml_offset in DEV_DATA:
    spacy_matcher_offset = list()
    doc = nlp(xml_paragraph)
    for start_offset, end_offset, type_name in xml_offset:
        # https://spacy.io/usage/linguistic-features#section-named-entities
        span_doc = doc.char_span(start_offset, end_offset, label=type_name)
        if span_doc is not None:
            # span will be none if the word is incomplete
            spacy_matcher_offset.append(span_doc)
        else:
            print("ERROR char offset", doc.text[start_offset:end_offset])
    doc.ents = spacy_matcher_offset
    doc_annotated.append(doc)

# docs = convert_offsets_to_spacy_docs(doc_annotated, model_dir_path)
view_spacy_docs(doc_annotated)
