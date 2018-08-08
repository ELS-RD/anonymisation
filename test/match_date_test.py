from match_text.match_date import get_date


def test_date():
    assert get_date("le 12 janvier 2013 !") == [(3, 18, 'DATE_1')]
    assert get_date("le 12/01/2016 !") == [(3, 13, 'DATE_1')]
    assert get_date("le 12 / 01/2016 !") == [(3, 15, 'DATE_1')]
    assert get_date("le 12 / 01/16 !") == [(3, 13, 'DATE_1')]
    assert get_date("ARRÊT DU HUIT FÉVRIER DEUX MILLE TREIZE") == [(9, 39, 'DATE_1')]
    assert get_date("le 1er janvier 2013 !") == [(3, 19, 'DATE_1')]
    assert get_date("le 552-4-1 !") == []
