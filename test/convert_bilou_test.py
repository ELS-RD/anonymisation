from generate_trainset.convert_to_bilou import convert_unknown_bilou, convert_unknown_bilou_bulk
from ner.model_factory import get_empty_model
import pytest

pytest.nlp = get_empty_model(load_labels_for_training=True)


def test_bilou_conv():
    doc = pytest.nlp.make_doc("Ceci est un test.")
    offset1 = [(5, 8, "UNKNOWN")]
    assert convert_unknown_bilou(doc, offsets=offset1).ner == ['O', '-', 'O', 'O', 'O']
    assert convert_unknown_bilou_bulk([doc], [offset1])[0].ner == ['O', '-', 'O', 'O', 'O']
    offset2 = [(5, 8, "PARTIE_PP")]
    assert convert_unknown_bilou(doc, offsets=offset2).ner == ['O', 'U-PARTIE_PP', 'O', 'O', 'O']
