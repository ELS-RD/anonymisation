from generate_trainset.generate_names import remove_corp, get_family_name, get_title_case, get_company_names, \
    get_extended_extracted_name, random_case_change, get_extend_extracted_name_pattern


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
    assert get_company_names(text) == [(3, 22, 'PARTIE_PM'), (46, 71, 'PARTIE_PM')]


def test_extend_names():
    text = "Jessica SABBA épouse Mic Mac BENESTY"
    texts = [text]
    offsets = [[(7, 13, "PARTIE_PP"), (29, 36, "PARTIE_PP")]]
    pattern = get_extend_extracted_name_pattern(texts=texts, offsets=offsets)
    print(get_extended_extracted_name(text=text, pattern=pattern))
    assert get_extended_extracted_name(text=text, pattern=pattern) == [(0, 13, 'PARTIE_PP'), (21, 36, 'PARTIE_PP')]


def test_random_case_change():
    text = "La Banque est fermée"
    offsets = [(3, 9, "PARTIE_PP")]
    assert random_case_change(text, offsets, 100) == "La banque est fermée"
