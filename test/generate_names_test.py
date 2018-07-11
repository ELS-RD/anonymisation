from generate_trainset.first_name_dictionary import get_first_name_dict, get_first_name_matcher, get_first_name_matches
from generate_trainset.generate_names import remove_corp, get_last_name, get_title_case, get_company_names, \
    get_extended_extracted_name, random_case_change, get_extend_extracted_name_pattern, get_judge_name, get_clerk_name, \
    get_lawyer_name


def test_remove_corp_name():
    assert remove_corp("SA Toto") == "Toto"
    assert remove_corp("SA Toto Titi") == "Toto Titi"


def test_extract_family_name():
    assert get_last_name("Mic BEN TITI") == "BEN TITI"
    assert get_last_name("Mic BEN") == "BEN"
    assert get_last_name("Mic BENp") == ""


def test_title_case():
    assert get_title_case("mic ben toto") == "Mic Ben Toto"


def test_extract_company_names():
    text1 = "La Société TotoT Titi est responsable avec la SA Turl-ututu Et Consors de ce carnage."
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


def test_extract_judge_names():
    text1 = "sera jugé par Madame Bingo TOTO, Conseiller près la cour de machin chose"
    assert get_judge_name(text1) == [(21, 31, 'PRESIDENT')]
    text2 = "Monsieur Gilles BOURGEOIS, Conseiller faisant fonction de Président"
    assert get_judge_name(text2) == [(9, 25, 'PRESIDENT')]
    text3 = "Nous, Gilles BOURGEOIS, Conseiller faisant fonction de Président"
    assert get_judge_name(text3) == [(6, 22, 'PRESIDENT')]
    text4 = "Mme Véronique BEBON, Présidente"
    assert get_judge_name(text4) == [(4, 19, 'PRESIDENT')]
    text5 = "M. Gérard FORET DODELIN, Président"
    assert get_judge_name(text5) == [(3, 23, 'PRESIDENT')]
    text6 = "Madame Florence DELORD, Conseiller"
    assert get_judge_name(text6) == [(7, 22, 'PRESIDENT')]
    text7 = "Madame Frédérique BRUEL, Conseillère"
    assert get_judge_name(text7) == [(7, 23, 'PRESIDENT')]
    text8 = "devant M. Gérard FORET DODELIN, Président, chargé d'instruire l'affaire."
    assert get_judge_name(text8) == [(10, 30, 'PRESIDENT')]
    text9 = "représenté lors des débats par Madame POUEY, substitut général "
    assert get_judge_name(text9) == [(38, 43, 'PRESIDENT')]
    text10 = "devant Mme Véronique BEBON, Présidente, et Madame Frédérique BRUEL, Conseillère, chargées du rapport."
    assert get_judge_name(text10) == [(11, 26, 'PRESIDENT'), (50, 66, 'PRESIDENT')]
    text11 = "Mme Geneviève TOUVIER, présidente"
    assert get_judge_name(text11) == [(4, 21, 'PRESIDENT')]
    text12 = "Monsieur Michel WACHTER, conseiller,"
    assert get_judge_name(text12) == [(9, 23, 'PRESIDENT')]
    text13 = "- Michel FICAGNA, conseiller"
    assert get_judge_name(text13) == [(2, 16, 'PRESIDENT')]
    text14 = "Audience tenue par Florence PAPIN, conseiller, faisant "
    assert get_judge_name(text14) == [(19, 33, 'PRESIDENT')]


def test_extract_clerk_names():
    text = "Madame To TOTO, greffier"
    assert get_clerk_name(text) == [(7, 14, 'GREFFIER')]
    text2 = "assistée de Geneviève JAUFFRES, greffier"
    assert get_clerk_name(text2) == [(12, 30, 'GREFFIER')]
    text3 = "Cour d'Appel d'Aix en Provence, assisté de Josiane BOMEA, Greffier "
    assert get_clerk_name(text3) == [(43, 56, 'GREFFIER')]
    text4 = "Greffier lors des débats : Veronique SAIGE"
    assert get_clerk_name(text4) == [(27, 42, 'GREFFIER')]
    text5 = "Greffier lors des débats : Madame Françoise PARADIS DEISS."
    assert get_clerk_name(text5) == [(34, 57, 'GREFFIER')]
    text6 = "assistée de Geneviève JAUFFRES, greffière"
    assert get_clerk_name(text6) == [(12, 30, 'GREFFIER')]
    text7 = "GREFFIER : Mme Marie Estelle CHAPON"
    assert get_clerk_name(text7) == [(15, 35, 'GREFFIER')]


def test_extract_lawyer():
    text = "A la demande de Me Toto TOTO, avocat"
    assert get_lawyer_name(text) == [(19, 28, 'AVOCAT')]


def test_get_first_name_dict():
    first_name_dict = get_first_name_dict()
    assert len(first_name_dict) == 12469
    assert "Michaël " in first_name_dict
    assert "Michaël" not in first_name_dict


def test_get_phrase_matcher():
    text = "Aujourd'hui, Michaël et Jessica écrivent des unit tests dans la joie et la bonne humeur."
    first_name_matcher = get_first_name_matcher()
    print(get_first_name_matches(first_name_matcher, text))
    assert get_first_name_matches(first_name_matcher, text) == [(13, 20, 'PARTIE_PP'), (24, 31, 'PARTIE_PP')]
