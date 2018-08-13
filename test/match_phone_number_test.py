from match_text.match_phone import get_phone_number


def test_phone_number():
    assert get_phone_number("phone: (06)-42-92 72- 29 et 01 44 23 65 89") == [(8, 25, 'PHONE_NUMBER'),
                                                                              (28, 42, 'PHONE_NUMBER')]
    assert get_phone_number("phone: (06)-42-92 72- 29 + 12") == []
    assert get_phone_number("phone: (00)-42-92 72- 29 ") == []
