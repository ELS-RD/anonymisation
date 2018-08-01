from generate_trainset.build_dict_from_recognized_entities import get_frequent_entities_matcher, \
    get_frequent_entities_matches
from generate_trainset.match_courts import CourtName
from generate_trainset.match_date import get_date
from generate_trainset.extend_names import ExtendNames
from generate_trainset.extract_header_values import parse_xml_header
from generate_trainset.match_first_name_dictionary import FirstName
from generate_trainset.match_acora import get_matches
from generate_trainset.match_header import MatchValuesFromHeaders
from generate_trainset.match_patterns import get_company_names, \
    get_judge_name, get_clerk_name, \
    get_lawyer_name, get_addresses, get_partie_pp, get_all_name_variation, \
    find_address_in_block_of_paragraphs, get_juridictions, get_bar
from generate_trainset.match_rg import MatchRg
from generate_trainset.modify_strings import get_last_name, \
    get_first_last_name
from resources.config_provider import get_config_default


def test_find_address_in_paragraph_block():
    texts = ["popo", "Zone Industrielle de Rossignol", "47110 SAINTE LIVRADE SUR LOT", "popo", "", "", "", "", "", "",
             "", "", "", ""]
    offsets1 = [[], [], [], [], [], [], [], []]
    new_offsets = find_address_in_block_of_paragraphs(texts=texts, offsets=offsets1)
    expected_result = [[], [(0, 30, 'ADRESSE')], [(0, 28, 'ADRESSE')], [], [], [], [], []]
    offsets3 = [[], [], [(0, 28, 'ADRESSE')], [], [], [], [], []]
    offsets4 = [[], [(0, 30, 'ADRESSE')], [], [], [], [], [], []]
    assert new_offsets == expected_result
    new_offsets2 = find_address_in_block_of_paragraphs(texts=texts, offsets=expected_result)
    assert new_offsets2 == expected_result
    new_offsets3 = find_address_in_block_of_paragraphs(texts=texts, offsets=offsets3)
    assert new_offsets3 == expected_result
    new_offsets4 = find_address_in_block_of_paragraphs(texts=texts, offsets=offsets4)
    assert new_offsets4 == expected_result


def test_match_sub_pattern():
    texts = ["Je suis avec Jessica BENESTY et elle est sympa.",
             "Jessica n'est pas là.",
             "Ou est Mme. Benesty ?",
             "La SARL TOTO forme avec la SCI TOTO un groupe de sociétés.",
             "Condamné CEK PARTICIPATIONS à payer à la SCI CEK PARTICIPATIONS la somme"]
    offsets = [[(13, 28, "PARTIE_PP")], [], [], [(3, 12, "PARTIE_PM")], [(41, 63, "PARTIE_PM")]]
    assert get_all_name_variation(texts, offsets, threshold_span_size=4) == [[(13, 20, 'PARTIE_PP'),
                                                                              (13, 28, 'PARTIE_PP'),
                                                                              (21, 28, 'PARTIE_PP'),
                                                                              (13, 28, 'PARTIE_PP')],
                                                                             [(0, 7, 'PARTIE_PP')],
                                                                             [(12, 19, 'PARTIE_PP')],
                                                                             [(3, 12, 'PARTIE_PM'),
                                                                              (8, 12, 'PARTIE_PM'),
                                                                              (31, 35, 'PARTIE_PM'),
                                                                              (3, 12, 'PARTIE_PM')],
                                                                             [(9, 27, 'PARTIE_PM'),
                                                                              (41, 63, 'PARTIE_PM'),
                                                                              (45, 63, 'PARTIE_PM'),
                                                                              (41, 63, 'PARTIE_PM')]]


def test_extract_judge_names():
    text1 = "sera jugé par Madame Bingo TOTO, Conseiller près la cour de machin chose"
    assert get_judge_name(text1) == [(21, 31, 'MAGISTRAT')]
    text2 = "Monsieur Gilles BOURGEOIS, Conseiller faisant fonction de Président"
    assert get_judge_name(text2) == [(9, 25, 'MAGISTRAT')]
    text3 = "Nous, Gilles BOURGEOIS, Conseiller faisant fonction de Président"
    assert get_judge_name(text3) == [(6, 22, 'MAGISTRAT')]
    text4 = "Mme Véronique BEBON, Présidente"
    assert get_judge_name(text4) == [(4, 19, 'MAGISTRAT')]
    text5 = "M. Gérard FORET DODELIN, Président"
    assert get_judge_name(text5) == [(3, 23, 'MAGISTRAT')]
    text6 = "Madame Florence DELORD, Conseiller"
    assert get_judge_name(text6) == [(7, 22, 'MAGISTRAT')]
    text7 = "Madame Frédérique BRUEL, Conseillère"
    assert get_judge_name(text7) == [(7, 23, 'MAGISTRAT')]
    text8 = "devant M. Gérard FORET DODELIN, Président, chargé d'instruire l'affaire."
    assert get_judge_name(text8) == [(10, 30, 'MAGISTRAT')]
    text9 = "représenté lors des débats par Madame POUEY, substitut général "
    assert get_judge_name(text9) == [(38, 43, 'MAGISTRAT')]
    text10 = "devant Mme Véronique BEBON, Présidente, et Madame Frédérique BRUEL, Conseillère, chargées du rapport."
    assert get_judge_name(text10) == [(11, 26, 'MAGISTRAT'), (50, 66, 'MAGISTRAT')]
    text11 = "Mme Geneviève TOUVIER, présidente"
    assert get_judge_name(text11) == [(4, 21, 'MAGISTRAT')]
    text12 = "Monsieur Michel WACHTER, conseiller,"
    assert get_judge_name(text12) == [(9, 23, 'MAGISTRAT')]
    text13 = "- Michel FICAGNA, conseiller"
    assert get_judge_name(text13) == [(2, 16, 'MAGISTRAT')]
    text14 = "Audience tenue par Florence PAPIN, conseiller, faisant "
    assert get_judge_name(text14) == [(19, 33, 'MAGISTRAT')]
    text15 = "Vincent NICOLAS, Conseiller"
    assert get_judge_name(text15) == [(0, 15, 'MAGISTRAT')]
    text16 = "2016, Monsieur Hubert de BECDELIEVRE, président de chambre"
    assert get_judge_name(text16) == [(15, 36, 'MAGISTRAT')]
    text17 = "Conseiller : Mélanie FILIATREAU"
    assert get_judge_name(text17) == [(13, 31, 'MAGISTRAT')]
    text18 = "Présidente : Mme Mélanie FILIATREAU"
    assert get_judge_name(text18) == [(17, 35, 'MAGISTRAT')]
    text19 = "Monsieur Benoît HOLLEAUX, conseiller faisant fonction de président"
    assert get_judge_name(text19) == [(9, 24, 'MAGISTRAT')]
    text20 = "Présidée par Isabelle BORDENAVE, Conseiller, magistrat rapporteur, qui en a rendu compte à la Cour."
    assert get_judge_name(text20) == [(13, 31, 'MAGISTRAT')]
    text21 = "Madame Françoise AYMES BELLADINA, conseiller faisant fonction de président de chambre"
    assert get_judge_name(text21) == [(7, 32, 'MAGISTRAT')]
    text22 = "outre elle même, de Daniel TROUVE, premier président, et "
    assert get_judge_name(text22) == [(20, 33, 'MAGISTRAT')]
    text23 = "Nous, Françoise GILLY ESCOFFIER, Conseiller de la Mise en Etat de la 10e Chambre de la Cour d'Appel " \
             "d'Aix en Provence, assistée de GENEVIÈVE JAUFFRES, Greffier"
    assert get_judge_name(text23) == [(6, 31, 'MAGISTRAT')]
    text24 = "Nous, Anne VIDAL, Magistrat de la Mise en Etat de la 6e Chambre D de la Cour D'appel D'aix En Provence, " \
             "assisté de Dominique COSTE, Greffier,"
    assert get_judge_name(text24) == [(6, 16, 'MAGISTRAT')]
    text25 = "Monsieur Gilles BOURGEOIS, Conseiller faisant fonction de Président"
    assert get_judge_name(text25) == [(9, 25, 'MAGISTRAT')]


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
    text8 = 'Arrêt signé par Monsieur LE GALLO, Président et par Madame HAON, Greffier.'
    assert get_clerk_name(text8) == [(59, 63, 'GREFFIER')]


def test_extract_lawyer():
    text1 = "A la demande de Me Toto TOTO, avocat"
    assert get_lawyer_name(text1) == [(19, 28, 'AVOCAT')]
    text2 = "Me Carine Chevalier - Kasprzak"
    assert get_lawyer_name(text2) == [(3, 30, 'AVOCAT')]


def test_get_first_name_dict():
    matcher = FirstName(ignore_case=False)
    assert len(matcher.first_name_dict) == 12464
    assert "Michaël" in matcher.first_name_dict


def test_get_phrase_matcher():
    text = "Aujourd'hui, Michaël et Jessica écrivent des unit tests dans la joie et la bonne humeur, " \
           "mais où sont donc les enfants ?"
    matcher = FirstName(ignore_case=False)
    assert matcher.get_matches(text=text) == [(13, 19, 'PARTIE_PP'), (24, 30, 'PARTIE_PP')]
    assert matcher.contain_first_names(text=text) is True


def test_get_address():
    text1 = "avant 130-140, rue Victor HUGO - 123456 Saint-Etienne après"
    assert get_addresses(text1) == [(6, 53, 'ADRESSE')]
    text2 = "avant 13 rue Ernest Renan après"
    assert get_addresses(text2) == [(6, len(text2) - 5, 'ADRESSE')]
    text3 = "avant 20 Avenue André Prothin après"
    assert get_addresses(text3) == [(6, len(text3) - 5, 'ADRESSE')]
    text4 = "avant 114 avenue Emile Zola après"
    assert get_addresses(text4) == [(6, len(text4) - 5, 'ADRESSE')]
    text5 = "avant 5 rue Jean Moulin après"
    assert get_addresses(text5) == [(6, len(text5) - 5, 'ADRESSE')]
    text6 = "avant 85, rue Gabriel Péri après"
    assert get_addresses(text6) == [(6, len(text6) - 5, 'ADRESSE')]
    text8 = "avant 3, rue Christophe Colomb après"
    assert get_addresses(text8) == [(6, len(text8) - 5, 'ADRESSE')]
    text9 = "avant 161, rue Andr Bisiaux - ZAC Solvay - Plateau de Haye après"
    assert get_addresses(text9) == [(6, len(text9) - 5, 'ADRESSE')]
    text10 = "avant 38, boulevard Georges Clémenceau après"
    assert get_addresses(text10) == [(6, len(text10) - 5, 'ADRESSE')]
    text11 = "avant 35, rue Maurice Flandin après"
    assert get_addresses(text11) == [(6, len(text11) - 5, 'ADRESSE')]
    text12 = "avant 22 rue Henri Rochefort - 75017 PARIS après"
    assert get_addresses(text12) == [(6, 42, 'ADRESSE')]
    text13 = "avant 14 Boulevard Marie et Alexandre Oyon - 72100 LE MANS après"
    assert get_addresses(text13) == [(6, 58, 'ADRESSE')]
    text14 = "avant allée Toto après"
    assert get_addresses(text14) == [(6, len(text14) - 5, 'ADRESSE')]
    text15 = "avant 14 Boulevard Marie et Alexandre Oyon après"
    assert get_addresses(text15) == [(6, len(text15) - 5, 'ADRESSE')]
    text16 = "avant 45, rue de Gironis après"
    assert get_addresses(text16) == [(6, 25, 'ADRESSE')]
    text17 = "avant 10 Boulevard Pasteur à BRY SUR MARNE après"
    assert get_addresses(text17) == [(6, 43, 'ADRESSE')]
    text18 = "un logement sis 1, rue d'Ebersheim à Strasbourg, moyennant"
    assert get_addresses(text18) == [(16, 47, 'ADRESSE')]
    text19 = "je me trouve Place de l'Étoile."
    assert get_addresses(text19) == [(13, 31, 'ADRESSE')]
    text20 = "je ne veux pas payer à la place de Madame Toto !"
    assert get_addresses(text20) == []
    text21 = "je ne veux pas payer en lieu et place de Madame Toto !"
    assert get_addresses(text21) == []
    text22 = "avant, 130/ 140, rue Victor HUGO    - 123456 Saint-Etienne après"
    assert get_addresses(text22) == [(7, 58, 'ADRESSE')]
    text23 = "demeurant 385 rue de Lyon - BP 70004 - 13015 MARSEILLE après"
    assert get_addresses(text23) == [(10, 54, 'ADRESSE')]
    text24 = "demeurant 9 avenue Désambrois Palais Stella - 06000 NICE après"
    assert get_addresses(text24) == [(10, 56, 'ADRESSE')]
    text25 = "demeurant 9 Avenue Desambrois - 06000 NICE FORNASERO SAS, 20 rue De France 06000 Fornasero après"
    assert get_addresses(text25) == [(10, 56, 'ADRESSE'), (58, 90, 'ADRESSE')]
    text26 = "demeurant 61 avenue Halley - 59866 VILLENEUVE D'ASQ CEDEX après"
    assert get_addresses(text26) == [(10, 57, 'ADRESSE')]
    text27 = "Réf : 35057719643, demeurant 6 rue du Professeur LAVIGNOLLE - BP 189 - 33042 BORDEAUX CEDEX après"
    assert get_addresses(text27) == [(29, 91, 'ADRESSE')]
    text28 = "demeurant 26 RUE DE MULHOUSE - BP 77837 - 21078 DIJON CEDEX après"
    assert get_addresses(text28) == [(10, 59, 'ADRESSE')]
    text29 = "demeurant 61 avenue de la Grande Bégude - RN 96 - 13770 VENELLES"
    assert get_addresses(text29) == [(10, 64, 'ADRESSE')]


# def test_get_postal_code_city():
#     matcher = PostalCodeCity()
#     assert matcher.get_matches(text="avant 67000 Strasbourg après") == [(6, 22, 'ADRESSE')]


def test_match_patterns():
    config_training = get_config_default()
    xml_path = config_training["xml_unittest_file"]
    header_content_all_cases = parse_xml_header(path=xml_path)
    case_id = list(header_content_all_cases.keys())[0]
    header_content = header_content_all_cases[case_id]
    headers_matcher = MatchValuesFromHeaders(current_header=header_content, threshold_size=3)
    matcher_partie_pp = headers_matcher.get_matcher_of_partie_pp_from_headers()

    text1 = "C'est Catherine ***REMOVED*** qui est responsable de ces faits avec M. LEON ***REMOVED***"

    assert get_matches(matcher_partie_pp, text1, "PARTIE_PP") == [(6, 22, 'PARTIE_PP')]

    text2 = "Me Touboul s'avance avec Patrice Cipre pendant que la greffière, Mme. Laure Metge, prend des notes"
    # TODO review tests (code is now very strict, does these tests make sense?)
    # matcher_lawyers = headers_matcher.get_matcher_of_lawyers_from_headers()
    # assert get_matches(matcher_lawyers, text2, "AVOCAT") == [(3, 10, 'AVOCAT'),
    #                                                          (25, 32, 'AVOCAT'),
    #                                                          (25, 38, 'AVOCAT'),
    #                                                          (33, 38, 'AVOCAT')]

    # matcher_clerks = headers_matcher.get_matcher_of_clerks_from_headers()
    # assert get_matches(matcher_clerks, text2, "GREFFIER") == [(70, 75, 'GREFFIER'),
    #                                                           (70, 81, 'GREFFIER'),
    #                                                           (76, 81, 'GREFFIER')]


def test_match_partie_pp_regex():
    text1 = "- Toto Popo né le 30"
    assert get_partie_pp(text1) == [(2, 11, 'PARTIE_PP')]
    text2 = "- Toto Popo, né le 30"
    assert get_partie_pp(text2) == [(2, 11, 'PARTIE_PP')]
    text3 = "- Vanessa née le 1er octobre 1987 a TOULON (Var),"
    assert get_partie_pp(text3) == [(2, 9, 'PARTIE_PP')]
    text4 = "•   Eugène né le 23 mars 1997 à Grenoble ( 38"
    assert get_partie_pp(text4) == [(4, 10, 'PARTIE_PP')]
    text5 = "Elle ajoute que les sommes réclamées ne seraient éventuellement " \
            "dues que pour les années 2016 et suivantes"
    assert get_partie_pp(text5) == []
    text6 = "Je vois les consorts Toto BOBO au loin."
    assert get_partie_pp(text6) == [(21, 30, 'PARTIE_PP')]
    text7 = "Ne serait-ce pas le Docteur Toto BOBO au loin."
    assert get_partie_pp(text7) == [(28, 37, 'PARTIE_PP')]
    text8 = "C'est Madame Titi Toto épouse POPO PIPI"
    assert get_partie_pp(text8) == [(13, 39, 'PARTIE_PP')]
    text9 = "C'est Madame Titi épouse POPO qui est là"
    assert get_partie_pp(text9) == [(13, 29, 'PARTIE_PP')]
    text10 = "C'est Madame TOTO épouse Popo"
    assert get_partie_pp(text10) == [(13, 29, 'PARTIE_PP')]
    text11 = 'Par déclaration du 24 janvier 2011 Dominique FELLMANN et Marie Reine PIERRE épouse FELLMANN ont '
    assert get_partie_pp(text11) == [(57, 91, 'PARTIE_PP')]


def test_extract_company_names():
    text1 = "La Société TotoT Titi est responsable avec la SA Turl-ututu Et Consors de ce carnage."
    assert get_company_names(text1) == [(3, 21, 'PARTIE_PM'), (46, 70, 'PARTIE_PM')]
    text2 = "Vu l'absence de l'Association pour l'Insertion et l'Accompagnement en Limousin (ASIIAL) assignée ;"
    assert get_company_names(text2) == [(18, 87, 'PARTIE_PM')]
    text3 = "Condamner solidairement les Sociétés OCM et OCS aux entiers dépens."
    assert get_company_names(text3) == [(28, 47, 'PARTIE_PM')]
    text4 = "La SARL ENZO & ROSSO n'est pas facile à extraire."
    assert get_company_names(text4) == [(3, 20, 'PARTIE_PM')]
    text5 = "la Caisse Nationale des Caisses d'Epargne était "
    assert get_company_names(text5) == [(3, 41, "PARTIE_PM")]
    text6 = "le Syndicat des Copropriétaires de la Résidence Le Jardin de la Galère, ce qui"
    assert get_company_names(text6) == [(3, 70, "PARTIE_PM")]
    text7 = "SA CAISSE D'EPARGNE ET DE PREVOYANCE PROVENCE ALPES C ORSE LA CAISSE D'EPARGNE ET, " \
            "Banque coopérative"
    assert get_company_names(text7) == [(0, 81, "PARTIE_PM")]


def test_extend_names():
    text1 = "Mme Jessica SABBA épouse M. Mic Mac BENESTY"
    texts1 = [text1]
    offsets1 = [[(12, 17, "PARTIE_PP"), (36, 43, "PARTIE_PP")]]
    offset_expected_result = [(4, 17, 'PARTIE_PP'), (28, 43, 'PARTIE_PP')]
    pattern1 = ExtendNames(texts=texts1, offsets=offsets1, type_name='PARTIE_PP')
    assert pattern1.get_extended_names(text=text1) == offset_expected_result

    assert ExtendNames.get_extended_extracted_name_multiple_texts(texts=texts1,
                                                                  offsets=offsets1,
                                                                  type_name='PARTIE_PP') == [[(4, 17, 'PARTIE_PP'),
                                                                                              (28, 43, 'PARTIE_PP'),
                                                                                              (12, 17, 'PARTIE_PP'),
                                                                                              (36, 43, 'PARTIE_PP')]]

    text2 = "Le testament de Wolfgang REUTHER est établi en Allemagne."
    texts2 = [text2]
    offsets2 = [[(25, 32, "PARTIE_PP")]]
    # Should not match because it is not preceded by Monsieur / Madame
    expected_offsets2 = []
    pattern2 = ExtendNames(texts=texts2, offsets=offsets2, type_name='PARTIE_PP')
    assert pattern2.get_extended_names(text=text2) == expected_offsets2
    text3 = "Monsieur Ludovic Frédéric Jean Nicolas REUTHER, majeur protégé"
    texts3 = [text3]
    offsets3 = [[(9, 16, "PARTIE_PP"), (39, 46, "PARTIE_PP")]]
    offset_expected_result3 = [(9, 46, "PARTIE_PP")]
    pattern3 = ExtendNames(texts=texts3, offsets=offsets3, type_name='PARTIE_PP')
    assert pattern3.get_extended_names(text=text3) == offset_expected_result3
    text4 = text3
    texts4 = texts3
    offsets4 = [[(9, 16, "PARTIE_PP")]]
    offset_expected_result4 = offset_expected_result3
    pattern4 = ExtendNames(texts=texts4, offsets=offsets4, type_name='PARTIE_PP')
    assert pattern4.get_extended_names(text=text4) == offset_expected_result4
    text5 = "Ludovic Frédéric Jean Nicolas REUTHER, majeur protégé"
    texts5 = [text5]
    offsets5 = [[(8, 16, "PARTIE_PP")]]
    offset_expected_result5 = [(8, 37, 'PARTIE_PP')]
    pattern5 = ExtendNames(texts=texts5, offsets=offsets5, type_name='PARTIE_PP')
    assert pattern5.get_extended_names(text=text5) == offset_expected_result5
    text6 = "EDF - DCPP MEDITERRANEE"
    texts6 = [text6]
    offsets6 = [[(0, 3, "PARTIE_PM")]]
    offset_expected_result6 = [(0, 23, 'PARTIE_PM')]
    pattern6 = ExtendNames(texts=texts6, offsets=offsets6, type_name='PARTIE_PM')
    assert pattern6.get_extended_names(text=text6) == offset_expected_result6


def test_extract_family_name():
    assert get_last_name("Mic BEN TITI") == "BEN TITI"
    assert get_last_name(" Mic BEN TITI ") == "BEN TITI"
    assert get_last_name("Mic BEN") == "BEN"
    assert get_last_name("Mic BENp") == ""
    assert get_first_last_name("Mic BEN TITI") == ("Mic", "BEN TITI")
    assert get_first_last_name(" Mic BEN TITI ") == ("Mic", "BEN TITI")


def test_frequent_entities():
    freq_entities = {"benesty": "AVOCAT", "jessica": "PARTIE_PP"}
    matcher = get_frequent_entities_matcher(content=freq_entities)
    text = "Me Benesty rencontre son client Jessica."
    assert get_frequent_entities_matches(matcher=matcher, frequent_entities_dict=freq_entities, text=text) == \
           [(3, 10, 'AVOCAT'), (32, 39, 'PARTIE_PP')]


def test_extract_court_name():
    text1 = "LA COUR D'APPEL D'AGEN, 1ère chambre dans l'affaire,"
    assert get_juridictions(text=text1) == [(3, 22, 'JURIDICTION')]
    text2 = "Par jugement en date du 21 janvier 2003, le tribunal correctionnel de Mulhouse a"
    assert get_juridictions(text=text2) == [(44, 79, 'JURIDICTION')]
    text3 = "COUR D'APPEL D'AIX EN PROVENCE N. TRUC"
    assert get_juridictions(text=text3) == [(0, 32, 'JURIDICTION')]
    text4 = "ARRET DE LA COUR D'APPEL D'AIX EN PROVENCE DU TRENTE AOUT"
    assert get_juridictions(text=text4) == [(12, 42, 'JURIDICTION')]
    text5 = "par le conseil de prud'hommes d'Aix en Provence après"
    assert get_juridictions(text=text5) == [(7, 48, 'JURIDICTION')]


def test_match_court_name():
    matcher = CourtName()
    text1 = "LA COUR D'Appel de Paris"
    assert matcher.get_matches(text=text1) == [(3, 24, 'JURIDICTION')]


def test_date():
    assert get_date("le 12 janvier 2013 !") == [(3, 18, 'DATE')]
    assert get_date("le 12/01/2016 !") == [(3, 13, 'DATE')]
    assert get_date("le 12 / 01/2016 !") == [(3, 15, 'DATE')]
    assert get_date("le 12 / 01/16 !") == [(3, 13, 'DATE')]
    assert get_date("ARRÊT DU HUIT FÉVRIER DEUX MILLE TREIZE") == [(9, 39, 'DATE')]
    assert get_date("le 1er janvier 2013 !") == [(3, 19, 'DATE')]


def test_bar():
    text1 = "Le barreau de PARIS toto"
    assert get_bar(text=text1) == [(3, 19, 'BARREAU')]
    text2 = "Je travaille au barreau D'AMIENS et c'est top !"
    assert get_bar(text=text2) == [(16, 32, 'BARREAU')]


def test_rg():
    text1 = "CA-aix-en-provence-20130208-1022871-jurica"
    matcher = MatchRg(case_id=text1)
    assert matcher.get_rg_from_case_id() == "1022871"
    assert matcher.get_rg_offset_from_text(text=text1) == [(28, 35, 'RG')]
    text2 = "Le numéro RG est celui-ci 102 /2871."
    assert matcher.get_rg_offset_from_text(text=text2) == [(26, 35, 'RG')]
