from match_text.match_credit_card import get_credit_card_number


def test_credit_card():
    credit_card_valid = "4474 2054 6736 1295"
    credit_card_invalid = "1265 157309414560"

    assert get_credit_card_number("pop " + credit_card_valid + " apres") == [(4, 24, 'CREDIT_CARD')]
    assert get_credit_card_number("pop " + credit_card_invalid + " apres") == []
    assert get_credit_card_number("1234 1234 1234 1234") == []
    assert get_credit_card_number("1- 1234 1234 1234 1234") == []
    assert get_credit_card_number("1- " + credit_card_valid) == []
