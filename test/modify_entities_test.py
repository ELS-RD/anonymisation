from random import seed

from modify_text.change_case import get_title_case, random_case_change, change_random_word_case
from modify_text.modify_strings import remove_org_type, remove_key_words


def test_remove_corp_name():
    assert remove_org_type("SA Toto") == "Toto"
    assert remove_org_type("SA Toto Titi") == "Toto Titi"


def test_title_case():
    assert get_title_case("mic ben toto") == "Mic Ben Toto"


def test_random_case_change():
    text = "La Banque est fermée"
    offsets = [(3, 9, "PERS")]
    seed(123)
    results = [random_case_change(text, offsets, 100) for _ in range(1, 500)]

    assert "La Banque est fermée" in results
    assert "La banque est fermée" in results
    assert "La BANQUE est fermée" in results


def test_random_case_change_word_level():
    seed(123)
    text = "La Banque est fermée"
    results = [change_random_word_case(text) for _ in range(1, 500)]
    assert "LA Banque EST fermée" in results


def test_remove_key_words():
    text = "Ayant pour conseil Me Myriam MASSENGO LACAVE et Me Toto TITI, " \
           "avocat au barreau de PARIS, toque: B1132"
    offsets = [(22, 44, "LAWYER"), (51, 60, "LAWYER")]
    assert remove_key_words(text=text, offsets=offsets, rate=100) == ('Ayant pour conseil Myriam MASSENGO LACAVE '
                                                                      'et Toto TITI, avocat au barreau de PARIS, '
                                                                      'toque: B1132',
                                                                      [(19, 41, "LAWYER"),
                                                                       (45, 54, "LAWYER")])

    assert remove_key_words(text=text, offsets=offsets, rate=0) == (text, offsets)
