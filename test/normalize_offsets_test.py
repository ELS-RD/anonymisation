from generate_trainset.normalize_offset import normalize_offsets, remove_offset_space


def test_normalize_offsets():
    data1 = [(5, 10, 'AVOCAT'), (18, 24, 'PARTIE_PM'), (22, 24, 'PARTIE_PM'), (120, 133, 'AVOCAT')]
    assert normalize_offsets(data1) == [(5, 10, 'AVOCAT'), (18, 24, 'PARTIE_PM'), (120, 133, 'AVOCAT')]
    data2 = [(71, 75, 'PARTIE_PP'), (77, 85, 'PARTIE_PP')]
    assert normalize_offsets(data2) == [(71, 85, 'PARTIE_PP')]
    data3 = [(5, 10, 'AVOCAT'), (71, 75, 'PARTIE_PP'), (77, 85, 'PARTIE_PP'), (120, 133, 'AVOCAT')]
    assert normalize_offsets(data3) == [(5, 10, 'AVOCAT'), (71, 85, 'PARTIE_PP'), (120, 133, 'AVOCAT')]
    data4 = [(5, 10, 'AVOCAT'), (77, 85, 'PARTIE_PP'), (77, 85, 'PARTIE_PP'), (120, 133, 'AVOCAT')]
    assert normalize_offsets(data4) == [(5, 10, 'AVOCAT'), (77, 85, 'PARTIE_PP'), (120, 133, 'AVOCAT')]
    data5 = [(16, 20, 'PARTIE_PP'), (22, 30, 'PARTIE_PP')]
    assert normalize_offsets(data5) == [(16, 30, 'PARTIE_PP')]
    data6 = [(10, 21, 'PARTIE_PP'), (22, 30, 'PARTIE_PP')]
    assert normalize_offsets(data6) == [(10, 30, 'PARTIE_PP')]
    data7 = []
    assert normalize_offsets(data7) == []
    data8 = [(1, 1, "PARTIE_PP")]
    assert normalize_offsets(data8) == []
    data9 = [(1, 3, "PARTIE_PP")]
    assert normalize_offsets(data9) == []
    data10 = [(1, 10, "PARTIE_PP"), (1, 10, "PARTIE_PP"), (3, 10, "PARTIE_PP")]
    assert normalize_offsets(data10) == [(1, 10, "PARTIE_PP")]


def test_remove_spaces():
    text = "Je suis ici et je programme."
    offset = [(3, 8, "TEST")]
    span_original = text[offset[0][0]:offset[0][1]]
    assert span_original == "suis "
    new_offset = remove_offset_space(text, offset)
    span_new = text[new_offset[0][0]:new_offset[0][1]]
    assert span_new == span_original.strip()
