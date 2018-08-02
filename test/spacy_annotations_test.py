from spacy.tokens.doc import Doc

from generate_trainset.build_entity_dictionary import EntityTypename
from generate_trainset.convert_to_bilou import convert_unknown_bilou, convert_unknown_bilou_bulk
from ner.model_factory import get_empty_model
import pytest

pytest.nlp = get_empty_model(load_labels_for_training=True)


def test_bilou_conv():
    doc: Doc = pytest.nlp.make_doc("Ceci est un test.")
    offset1 = [(5, 8, "UNKNOWN")]
    assert convert_unknown_bilou(doc, offsets=offset1).ner == ['O', '-', 'O', 'O', 'O']
    assert convert_unknown_bilou_bulk([doc], [offset1])[0].ner == ['O', '-', 'O', 'O', 'O']
    offset2 = [(5, 8, "PERS")]
    assert convert_unknown_bilou(doc, offsets=offset2).ner == ['O', 'U-PERS', 'O', 'O', 'O']


def test_build_entity_dict():
    doc: Doc = pytest.nlp.make_doc("Ceci est un test.")
    span_doc = doc.char_span(5, 8, label="UNKNOWN")
    doc.ents = [span_doc]
    entity_typename = EntityTypename()
    entity_typename.add_spacy_entities(doc)
    assert entity_typename.get_dict() == {'est': 'UNKNOWN'}
