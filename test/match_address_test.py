from match_text.match_address import get_addresses, find_address_in_block_of_paragraphs, clean_address_offset, \
    clean_address_offsets


def test_get_address():
    text1 = "avant 130-140, rue Victor HUGO - 123456 Saint-Etienne après"
    assert get_addresses(text1) == [(6, 53, "ADDRESS_1")]
    text2 = "avant 13 rue Ernest Renan après"
    assert get_addresses(text2) == [(6, len(text2) - 5, "ADDRESS_1")]
    text3 = "avant 20 Avenue André Prothin après"
    assert get_addresses(text3) == [(6, len(text3) - 5, "ADDRESS_1")]
    text4 = "avant 114 avenue Emile Zola après"
    assert get_addresses(text4) == [(6, len(text4) - 5, "ADDRESS_1")]
    text5 = "avant 5 rue Jean Moulin après"
    assert get_addresses(text5) == [(6, len(text5) - 5, "ADDRESS_1")]
    text6 = "avant 85, rue Gabriel Péri après"
    assert get_addresses(text6) == [(6, len(text6) - 5, "ADDRESS_1")]
    text8 = "avant 3, rue Christophe Colomb après"
    assert get_addresses(text8) == [(6, len(text8) - 5, "ADDRESS_1")]
    text9 = "avant 161, rue Andr Bisiaux - ZAC Solvay - Plateau de Haye après"
    assert get_addresses(text9) == [(6, len(text9) - 5, "ADDRESS_1")]
    text10 = "avant 38, boulevard Georges Clémenceau après"
    assert get_addresses(text10) == [(6, len(text10) - 5, "ADDRESS_1")]
    text11 = "avant 35, rue Maurice Flandin après"
    assert get_addresses(text11) == [(6, len(text11) - 5, "ADDRESS_1")]
    text12 = "avant 22 rue Henri Rochefort - 75017 PARIS après"
    assert get_addresses(text12) == [(6, 42, "ADDRESS_1")]
    text13 = "avant 14 Boulevard Marie et Alexandre Oyon - 72100 LE MANS après"
    assert get_addresses(text13) == [(6, 58, "ADDRESS_1")]
    text14 = "avant allée Toto après"
    assert get_addresses(text14) == [(6, len(text14) - 5, "ADDRESS_1")]
    text15 = "avant 14 Boulevard Marie et Alexandre Oyon après"
    assert get_addresses(text15) == [(6, len(text15) - 5, "ADDRESS_1")]
    text16 = "avant 45, rue de Gironis après"
    assert get_addresses(text16) == [(6, 25, "ADDRESS_1")]
    text17 = "avant 10 Boulevard Pasteur à BRY SUR MARNE après"
    assert get_addresses(text17) == [(6, 43, "ADDRESS_1")]
    text18 = "un logement sis 1, rue d'Ebersheim à Strasbourg, moyennant"
    assert get_addresses(text18) == [(16, 49, "ADDRESS_1")]  # TODO should be 47 instead of 49
    text19 = "je me trouve Place de l'Étoile."
    assert get_addresses(text19) == [(13, 31, "ADDRESS_1")]
    text20 = "je ne veux pas payer à la place de Madame Toto !"
    assert get_addresses(text20) == []
    text21 = "je ne veux pas payer en lieu et place de Madame Toto !"
    assert get_addresses(text21) == []
    text22 = "avant, 130/ 140, rue Victor HUGO    - 123456 Saint-Etienne après"
    assert get_addresses(text22) == [(7, 58, "ADDRESS_1")]
    text23 = "demeurant 385 rue de Lyon - BP 70004 - 13015 MARSEILLE après"
    assert get_addresses(text23) == [(10, 54, 'ADDRESS_1')]
    text24 = "demeurant 9 avenue Désambrois Palais Stella - 06000 NICE après"
    assert get_addresses(text24) == [(10, 56, "ADDRESS_1")]
    text25 = "demeurant 9 Avenue Desambrois - 06000 NICE FORNASERO SAS, 20 rue De France 06000 Fornasero après"
    assert get_addresses(text25) == [(10, 56, 'ADDRESS_1'), (10, 90, 'ADDRESS_1'), (58, 90, 'ADDRESS_1')]
    text26 = "demeurant 61 avenue Halley - 59866 VILLENEUVE D'ASQ CEDEX après"
    assert get_addresses(text26) == [(10, 57, "ADDRESS_1")]
    text27 = "Réf : 35057719643, demeurant 6 rue du Professeur LAVIGNOLLE - BP 189 - 33042 BORDEAUX CEDEX après"
    assert get_addresses(text27) == [(29, 91, "ADDRESS_1")]
    text28 = "demeurant 26 RUE DE MULHOUSE - BP 77837 - 21078 DIJON CEDEX après"
    assert get_addresses(text28) == [(10, 59, "ADDRESS_1")]
    text29 = "demeurant 61 avenue de la Grande Bégude - RN 96 - 13770 VENELLES"
    assert get_addresses(text29) == [(10, 64, "ADDRESS_1")]
    text30 = "20 place Jean Baptiste Durand"
    assert get_addresses(text30) == [(0, 29, "ADDRESS_1")]
    text31 = "demeurant au lieu dit de la Grande Bégude - RN 96 - 13770 VENELLES"
    assert get_addresses(text31) == [(28, 66, 'ADDRESS_1')]
    text32 = "demeurant 2 Avenue Jean Baptiste Galandy - 19100 BRIVE après"
    assert get_addresses(text32) == [(10, 54, 'ADDRESS_1')]
    text33 = "Profession : Retraité, demeurant Bourlioux - 19380 SAINT BONNET ELVERT"
    assert get_addresses(text33) == [(33, 70, 'ADDRESS_1')]
    text34 = "1 À 14, Bd Henri Sappia, 06100 Nice et"
    assert get_addresses(text34) == [(4, 35, 'ADDRESS_1')]
    text35 = "demeurant 9 avenue Désambrois Palais Stella À NICE après"
    assert get_addresses(text35) == [(10, 51, "ADDRESS_1")]
    text36 = "situé à Bormes Les Mimosas, cadastré section AA n° 477, situé"
    assert get_addresses(text36) == [(37, 54, "ADDRESS_1")]
    text37 = "les constructions semblent empiéter sur la parcelle cadastrée AO n° 122 appartenant, au cadastre, à la"
    assert get_addresses(text37) == [(62, 71, "ADDRESS_1")]
    text38 = "rangée de parpaings sous les tuiles aux lieu et place du toit en tôles ondulées"
    assert get_addresses(text38) == []



def test_find_address_in_paragraph_block():
    texts = ["popo", "Zone Industrielle de Rossignol", "47110 SAINTE LIVRADE SUR LOT", "popo", "", "", "", "", "", "",
             "", "", "", ""]
    offsets1 = [[], [], [], [], [], [], [], []]
    new_offsets = find_address_in_block_of_paragraphs(texts=texts, offsets=offsets1)
    expected_result = [[], [(0, 30, "ADDRESS")], [(0, 28, "ADDRESS")], [], [], [], [], []]
    offsets3 = [[], [], [(0, 28, "ADDRESS")], [], [], [], [], []]
    offsets4 = [[], [(0, 30, "ADDRESS")], [], [], [], [], [], []]
    assert new_offsets == expected_result
    new_offsets2 = find_address_in_block_of_paragraphs(texts=texts, offsets=expected_result)
    assert new_offsets2 == expected_result
    new_offsets3 = find_address_in_block_of_paragraphs(texts=texts, offsets=offsets3)
    assert new_offsets3 == expected_result
    new_offsets4 = find_address_in_block_of_paragraphs(texts=texts, offsets=offsets4)
    assert new_offsets4 == expected_result


def test_clean_address_offset():
    text1 = "Domiciliés ensemble :12 rue"
    assert clean_address_offset(text=text1, offsets=[(0, len(text1) - 1, "ADDRESS")]) == [(21, 26, 'ADDRESS')]
    text2 = "Demeurant 13 rue"
    assert clean_address_offset(text=text2, offsets=[(0, len(text2) - 1, "ADDRESS")]) == [(10, 15, 'ADDRESS')]
    assert clean_address_offsets(texts=[text2], offsets=[[(0, len(text2) - 1, "ADDRESS")]]) == [[(10, 15, 'ADDRESS')]]


# def test_get_postal_code_city():
#     matcher = PostalCodeCity()
#     assert matcher.get_matches(text="avant 67000 Strasbourg après") == [(6, 22, "ADDRESS")]
