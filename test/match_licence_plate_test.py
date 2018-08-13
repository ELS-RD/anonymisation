from match_text.match_licence_plate import get_licence_plate


def test_licence_plate():
    assert get_licence_plate("AA111AA") == [(0, 7, 'LICENCE_PLATE')]
    assert get_licence_plate("AA-111-AA") == [(0, 9, 'LICENCE_PLATE')]
    assert get_licence_plate("AA 111 AA") == [(0, 9, 'LICENCE_PLATE')]
    assert get_licence_plate("1 AA111AA") == []
    assert get_licence_plate("AA 111 AA 1") == []

    assert get_licence_plate("1AA11") == [(0, 5, 'LICENCE_PLATE')]
    assert get_licence_plate("9999 ZZZ 99") == [(0, 11, 'LICENCE_PLATE')]
    assert get_licence_plate("9999 ZZZ 999") == []
