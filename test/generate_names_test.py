from generate_trainset.generate_names import remove_corp, get_family_name, get_title_case


def test_remove_corp_name():
    assert remove_corp("SA Toto") == "Toto"


def test_extract_family_name():
    assert get_family_name("Mic BEN TITI") == "BEN TITI"
    assert get_family_name("Mic BEN") == "BEN"
    assert get_family_name("Mic BENp") == ""


def test_title_case():
    assert get_title_case("mic ben toto") == "Mic Ben Toto"
