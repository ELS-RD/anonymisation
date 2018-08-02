from generate_trainset.match_address import get_addresses, find_address_in_block_of_paragraphs


def test_get_address():
    text1 = "avant 130-140, rue Victor HUGO - 123456 Saint-Etienne après"
    assert get_addresses(text1) == [(6, 53, "ADDRESS")]
    text2 = "avant 13 rue Ernest Renan après"
    assert get_addresses(text2) == [(6, len(text2) - 5, "ADDRESS")]
    text3 = "avant 20 Avenue André Prothin après"
    assert get_addresses(text3) == [(6, len(text3) - 5, "ADDRESS")]
    text4 = "avant 114 avenue Emile Zola après"
    assert get_addresses(text4) == [(6, len(text4) - 5, "ADDRESS")]
    text5 = "avant 5 rue Jean Moulin après"
    assert get_addresses(text5) == [(6, len(text5) - 5, "ADDRESS")]
    text6 = "avant 85, rue Gabriel Péri après"
    assert get_addresses(text6) == [(6, len(text6) - 5, "ADDRESS")]
    text8 = "avant 3, rue Christophe Colomb après"
    assert get_addresses(text8) == [(6, len(text8) - 5, "ADDRESS")]
    text9 = "avant 161, rue Andr Bisiaux - ZAC Solvay - Plateau de Haye après"
    assert get_addresses(text9) == [(6, len(text9) - 5, "ADDRESS")]
    text10 = "avant 38, boulevard Georges Clémenceau après"
    assert get_addresses(text10) == [(6, len(text10) - 5, "ADDRESS")]
    text11 = "avant 35, rue Maurice Flandin après"
    assert get_addresses(text11) == [(6, len(text11) - 5, "ADDRESS")]
    text12 = "avant 22 rue Henri Rochefort - 75017 PARIS après"
    assert get_addresses(text12) == [(6, 42, "ADDRESS")]
    text13 = "avant 14 Boulevard Marie et Alexandre Oyon - 72100 LE MANS après"
    assert get_addresses(text13) == [(6, 58, "ADDRESS")]
    text14 = "avant allée Toto après"
    assert get_addresses(text14) == [(6, len(text14) - 5, "ADDRESS")]
    text15 = "avant 14 Boulevard Marie et Alexandre Oyon après"
    assert get_addresses(text15) == [(6, len(text15) - 5, "ADDRESS")]
    text16 = "avant 45, rue de Gironis après"
    assert get_addresses(text16) == [(6, 25, "ADDRESS")]
    text17 = "avant 10 Boulevard Pasteur à BRY SUR MARNE après"
    assert get_addresses(text17) == [(6, 43, "ADDRESS")]
    text18 = "un logement sis 1, rue d'Ebersheim à Strasbourg, moyennant"
    assert get_addresses(text18) == [(16, 47, "ADDRESS")]
    text19 = "je me trouve Place de l'Étoile."
    assert get_addresses(text19) == [(13, 31, "ADDRESS")]
    text20 = "je ne veux pas payer à la place de Madame Toto !"
    assert get_addresses(text20) == []
    text21 = "je ne veux pas payer en lieu et place de Madame Toto !"
    assert get_addresses(text21) == []
    text22 = "avant, 130/ 140, rue Victor HUGO    - 123456 Saint-Etienne après"
    assert get_addresses(text22) == [(7, 58, "ADDRESS")]
    text23 = "demeurant 385 rue de Lyon - BP 70004 - 13015 MARSEILLE après"
    assert get_addresses(text23) == [(10, 54, "ADDRESS")]
    text24 = "demeurant 9 avenue Désambrois Palais Stella - 06000 NICE après"
    assert get_addresses(text24) == [(10, 56, "ADDRESS")]
    text25 = "demeurant 9 Avenue Desambrois - 06000 NICE FORNASERO SAS, 20 rue De France 06000 Fornasero après"
    assert get_addresses(text25) == [(10, 56, "ADDRESS"), (58, 90, "ADDRESS")]
    text26 = "demeurant 61 avenue Halley - 59866 VILLENEUVE D'ASQ CEDEX après"
    assert get_addresses(text26) == [(10, 57, "ADDRESS")]
    text27 = "Réf : 35057719643, demeurant 6 rue du Professeur LAVIGNOLLE - BP 189 - 33042 BORDEAUX CEDEX après"
    assert get_addresses(text27) == [(29, 91, "ADDRESS")]
    text28 = "demeurant 26 RUE DE MULHOUSE - BP 77837 - 21078 DIJON CEDEX après"
    assert get_addresses(text28) == [(10, 59, "ADDRESS")]
    text29 = "demeurant 61 avenue de la Grande Bégude - RN 96 - 13770 VENELLES"
    assert get_addresses(text29) == [(10, 64, "ADDRESS")]
    text30 = "20 place Jean Baptiste Durand"
    assert get_addresses(text30) == [(0, 29, "ADDRESS")]


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


# def test_get_postal_code_city():
#     matcher = PostalCodeCity()
#     assert matcher.get_matches(text="avant 67000 Strasbourg après") == [(6, 22, "ADDRESS")]

