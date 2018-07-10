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
    text1 = "La Société TotoT Titi est responsable avec la SA Turl-ututu Et Consors de ce carnage."
    print(get_company_names(text1))
    assert get_company_names(text1) == [(3, 22, 'PARTIE_PM'), (46, 71, 'PARTIE_PM')]
    text2 = "Vu l'absence de l'Association pour l'Insertion et l'Accompagnement en Limousin (ASIIAL) assignée ;"
    assert get_company_names(text2) == [(18, 88, 'PARTIE_PM')]


def test_extend_names():
    text = "Mme Jessica SABBA épouse M. Mic Mac BENESTY"
    texts = [text]
    offsets = [[(11, 18, "PARTIE_PP"), (48, 55, "PARTIE_PP")]]
    pattern = get_extend_extracted_name_pattern(texts=texts, offsets=offsets, type_name_to_keep='PARTIE_PP')
    assert get_extended_extracted_name(text=text, pattern=pattern, type_name='PARTIE_PP') == [(4, 18, 'PARTIE_PP'),
                                                                                              (28, 43, 'PARTIE_PP')]


def test_random_case_change():
    text = "La Banque est fermée"
    offsets = [(3, 9, "PARTIE_PP")]
    assert random_case_change(text, offsets, 100) == "La banque est fermée"
