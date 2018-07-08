from generate_trainset.generate_names import remove_corp, get_family_name, get_title_case, get_company_names


def test_remove_corp_name():
    assert remove_corp("SA Toto") == "Toto"
    assert remove_corp("SA Toto Titi") == "Toto Titi"


def test_extract_family_name():
    assert get_family_name("Mic BEN TITI") == "BEN TITI"
    assert get_family_name("Mic BEN") == "BEN"
    assert get_family_name("Mic BENp") == ""


def test_title_case():
    assert get_title_case("mic ben toto") == "Mic Ben Toto"


def test_extract_company_names():
    text = "La Société TotoT Titi est responsable avec la SA Turl-ututu Et Consors de ce carnage."
    assert get_company_names(text) == [(3, 22, 'Société TotoT Titi '), (46, 71, 'SA Turl-ututu Et Consors ')]
