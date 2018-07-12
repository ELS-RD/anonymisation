from generate_trainset.normalize_offset import normalize_offsets


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
