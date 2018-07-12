from generate_trainset.extract_header_values import parse_xml_header
from generate_trainset.first_name_dictionary import get_first_name_dict, get_first_name_matcher, get_first_name_matches, \
    get_matches
from generate_trainset.match_patterns import get_last_name, get_company_names, \
    get_extended_extracted_name, get_extend_extracted_name_pattern, get_judge_name, get_clerk_name, \
    get_lawyer_name, get_addresses, get_list_of_partie_pp_from_headers_to_search, \
    get_list_of_lawyers_from_headers_to_search, \
    get_list_of_clerks_from_headers_to_search, get_partie_pp
from generate_trainset.modify_strings import get_title_case, random_case_change, remove_corp
from resources.config_provider import get_config_default


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
    text3 = "Condamner solidairement les Sociétés OCM et OCS aux entiers dépens."
    assert get_company_names(text3) == [(28, 48, 'PARTIE_PM')]


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

    results = [random_case_change(text, offsets, 100) for _ in range(1, 100)]

    assert "La Banque est fermée" in results
    assert "La banque est fermée" in results
    assert "La BANQUE est fermée" in results


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
    text15 = "Vincent NICOLAS, Conseiller"
    assert get_judge_name(text15) == [(0, 15, 'PRESIDENT')]
    text16 = "2016, Monsieur Hubert de BECDELIEVRE, président de chambre"
    assert get_judge_name(text16) == [(15, 36, 'PRESIDENT')]
    text17 = "Conseiller : Mélanie FILIATREAU"
    assert get_judge_name(text17) == [(13, 31, 'PRESIDENT')]
    text18 = "Présidente : Mme Mélanie FILIATREAU"
    assert get_judge_name(text18) == [(17, 35, 'PRESIDENT')]
    text19 = "Monsieur Benoît HOLLEAUX, conseiller faisant fonction de président"
    assert get_judge_name(text19) == [(9, 24, 'PRESIDENT')]


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
    assert get_first_name_matches(first_name_matcher, text) == [(13, 20, 'PARTIE_PP'), (24, 31, 'PARTIE_PP')]


def test_get_address():
    text1 = "avant 130-140, rue Victor HUGO    - 123456 Saint-Etienne après"
    assert get_addresses(text1) == [(5, len(text1) - 5, 'ADRESSE')]
    text2 = "avant 13 rue Ernest Renan après"
    assert get_addresses(text2) == [(5, len(text2) - 5, 'ADRESSE')]
    text3 = "avant 20 Avenue André Prothin après"
    assert get_addresses(text3) == [(5, len(text3) - 5, 'ADRESSE')]
    text4 = "avant 114 avenue Emile Zola après"
    assert get_addresses(text4) == [(5, len(text4) - 5, 'ADRESSE')]
    text5 = "avant 5 rue Jean Moulin après"
    assert get_addresses(text5) == [(5, len(text5) - 5, 'ADRESSE')]
    text6 = "avant 85, rue Gabriel Péri après"
    assert get_addresses(text6) == [(5, len(text6) - 5, 'ADRESSE')]
    text8 = "avant 3, rue Christophe Colomb après"
    assert get_addresses(text8) == [(5, len(text8) - 5, 'ADRESSE')]
    text9 = "avant 161, rue Andr Bisiaux - ZAC Solvay - Plateau de Haye après"
    assert get_addresses(text9) == [(5, len(text9) - 5, 'ADRESSE')]
    text10 = "avant 38, boulevard Georges Clémenceau après"
    assert get_addresses(text10) == [(5, len(text10) - 5, 'ADRESSE')]
    text11 = "avant 35, rue Maurice Flandin après"
    assert get_addresses(text11) == [(5, len(text11) - 5, 'ADRESSE')]
    text12 = "avant 22 rue Henri Rochefort - 75017 PARIS après"
    assert get_addresses(text12) == [(5, len(text12) - 5, 'ADRESSE')]
    text13 = "avant 14 Boulevard Marie et Alexandre Oyon - 72100 LE MANS après"
    assert get_addresses(text13) == [(5, len(text13) - 5, 'ADRESSE')]
    text14 = "avant allée Toto après"
    assert get_addresses(text14) == [(5, len(text14) - 5, 'ADRESSE')]


def test_match_patterns():
    config_training = get_config_default()
    xml_path = config_training["xml_unittest_file"]
    header_content_all_cases = parse_xml_header(path=xml_path)
    case_id = list(header_content_all_cases.keys())[0]
    header_content = header_content_all_cases[case_id]
    matcher_partie_pp = get_list_of_partie_pp_from_headers_to_search(header_content)
    text1 = "C'est Catherine ***REMOVED*** qui est responsable de ces faits avec M. LEON ***REMOVED***"
    assert get_matches(matcher_partie_pp, text1, "PARTIE_PP") == [(6, 22, 'PARTIE_PP'),
                                                                  (16, 22, 'PARTIE_PP'),
                                                                  (64, 77, 'PARTIE_PP')]
    text2 = "Me Touboul s'avance avec Patrice Cipre pendant que la greffière, Mme. Laure Metge, prend des notes"
    matcher_lawyers = get_list_of_lawyers_from_headers_to_search(header_content)
    assert get_matches(matcher_lawyers, text2, "AVOCAT") == [(3, 10, 'AVOCAT'),
                                                             (25, 38, 'AVOCAT'),
                                                             (33, 38, 'AVOCAT')]
    matcher_clerks = get_list_of_clerks_from_headers_to_search(header_content)
    assert get_matches(matcher_clerks, text2, "GREFFIER") == [(70, 81, 'GREFFIER'), (76, 81, 'GREFFIER')]


def test_match_partie_pp_regex():
    text1 = "- Toto Popo né le 30"
    assert get_partie_pp(text1) == [(2, 12, 'PARTIE_PP')]
    text2 = "- Toto Popo, né le 30"
    assert get_partie_pp(text2) == [(2, 11, 'PARTIE_PP')]
    text3 = "- Vanessa née le 1er octobre 1987 a TOULON (Var),"
    assert get_partie_pp(text3) == [(2, 10, 'PARTIE_PP')]
    text4 = "•   Eugène né le 23 mars 1997 à Grenoble ( 38"
    assert get_partie_pp(text4) == [(4, 11, 'PARTIE_PP')]
