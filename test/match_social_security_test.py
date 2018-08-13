from match_text.match_social_security_number import get_social_security_number


def test_social_security():
    valid_id = "2 40 09 93 618 017 05"
    invalid_id = "2 40 09 93 618 017 06"
    assert get_social_security_number(valid_id) == [(0, 21, 'SOCIAL_SECURITY_NUMBER')]
    assert get_social_security_number("1" + valid_id) == []
    assert get_social_security_number(invalid_id) == []
