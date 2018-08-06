from match_text_unsafe.extend_names import ExtendNames


def test_extend_names():
    text1 = "Mme Jessica SABBA épouse M. Mic Mac BENESTY"
    texts1 = [text1]
    offsets1 = [[(12, 17, "PERS"), (36, 43, "PERS")]]
    offset_expected_result = [(4, 17, "PERS"), (28, 43, "PERS")]
    pattern1 = ExtendNames(texts=texts1, offsets=offsets1, type_name="PERS")
    assert pattern1.get_extended_names(text=text1) == offset_expected_result

    assert ExtendNames.get_extended_extracted_name_multiple_texts(texts=texts1,
                                                                  offsets=offsets1,
                                                                  type_name="PERS") == [[(4, 17, "PERS"),
                                                                                              (28, 43, "PERS"),
                                                                                              (12, 17, "PERS"),
                                                                                              (36, 43, "PERS")]]

    text2 = "Le testament de Wolfgang REUTHER est établi en Allemagne."
    texts2 = [text2]
    offsets2 = [[(25, 32, "PERS")]]
    # Should not match because it is not preceded by Monsieur / Madame
    expected_offsets2 = []
    pattern2 = ExtendNames(texts=texts2, offsets=offsets2, type_name="PERS")
    assert pattern2.get_extended_names(text=text2) == expected_offsets2
    text3 = "Monsieur Ludovic Frédéric Jean Nicolas REUTHER, majeur protégé"
    texts3 = [text3]
    offsets3 = [[(9, 16, "PERS"), (39, 46, "PERS")]]
    offset_expected_result3 = [(9, 46, "PERS")]
    pattern3 = ExtendNames(texts=texts3, offsets=offsets3, type_name="PERS")
    assert pattern3.get_extended_names(text=text3) == offset_expected_result3
    text4 = text3
    texts4 = texts3
    offsets4 = [[(9, 16, "PERS")]]
    offset_expected_result4 = offset_expected_result3
    pattern4 = ExtendNames(texts=texts4, offsets=offsets4, type_name="PERS")
    assert pattern4.get_extended_names(text=text4) == offset_expected_result4
    text5 = "Ludovic Frédéric Jean Nicolas REUTHER, majeur protégé"
    texts5 = [text5]
    offsets5 = [[(8, 16, "PERS")]]
    offset_expected_result5 = [(8, 37, "PERS")]
    pattern5 = ExtendNames(texts=texts5, offsets=offsets5, type_name="PERS")
    assert pattern5.get_extended_names(text=text5) == offset_expected_result5
    text6 = "EDF - DCPP MEDITERRANEE"
    texts6 = [text6]
    offsets6 = [[(0, 3, "ORGANIZATION")]]
    offset_expected_result6 = [(0, 23, "ORGANIZATION")]
    pattern6 = ExtendNames(texts=texts6, offsets=offsets6, type_name="ORGANIZATION")
    assert pattern6.get_extended_names(text=text6) == offset_expected_result6

