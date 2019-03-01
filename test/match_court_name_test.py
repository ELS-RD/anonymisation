from match_text.match_courts import CourtName, get_juridictions


def test_extract_court_name():
    text1 = "LA COUR D'APPEL D'AGEN, 1ère chambre dans l'affaire,"
    assert get_juridictions(text=text1) == [(3, 22, "COURT_1")]
    text2 = "Par jugement en date du 21 janvier 2003, le tribunal correctionnel de Mulhouse a"
    assert get_juridictions(text=text2) == [(44, 79, "COURT_1")]
    text3 = "COUR D'APPEL D'AIX EN PROVENCE N. TRUC"
    assert get_juridictions(text=text3) == [(0, 32, "COURT_1")]
    text4 = "ARRET DE LA COUR D'APPEL D'AIX EN PROVENCE DU TRENTE AOUT"
    assert get_juridictions(text=text4) == [(12, 42, "COURT_1")]
    text5 = "par le conseil de prud'hommes d'Aix en Provence après"
    assert get_juridictions(text=text5) == [(7, 48, "COURT_1")]
    text6 = "par le conseil de prud'hommes d'Aix en Provence en l'an"
    assert get_juridictions(text=text6) == [(7, 47, "COURT_1")]


def test_match_court_name():
    matcher = CourtName()
    text1 = "LA COUR D'Appel de Paris"
    assert matcher.get_matches(text=text1) == [(3, 24, "COURT")]
