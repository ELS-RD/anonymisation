import regex

credit_card_regex = regex.compile(pattern="(?<!\d[[:punct:] ]*)"
                                          "\\b"
                                          "(\d[\- \.]*){16}"
                                          "\\b"
                                          "(?![[:punct:] ]*\d)",
                                  flags=regex.VERSION1)


def get_credit_card_number(text: str) -> list:
    pattern = credit_card_regex.search(text)
    if pattern is not None:
        number_as_string = text[pattern.start():pattern.end()]
        if validate(number_as_string):
            return [(pattern.start(), pattern.end(), "CREDIT_CARD")]
    return []


def sum_digits(digit):
    return digit if digit < 10 else (digit % 10) + (digit // 10)


def validate(credit_card_number_string: str):
    """
    https://www.pythoncircle.com/post/485/python-script-8-validating-credit-card-number-luhns-algorithm/
    :param credit_card_number_string:
    :return:
    """
    credit_card_number = ''.join(filter(lambda x: x.isdigit(), credit_card_number_string))
    if len(credit_card_number) != 16:
        return False

    # reverse the credit card number
    credit_card_number = credit_card_number[::-1]
    # convert to integer
    credit_card_number = [int(x) for x in credit_card_number]
    # double every second digit
    doubled_second_digit_list = list()
    digits = list(enumerate(credit_card_number, start=1))
    for index, digit in digits:
        if index % 2 == 0:
            doubled_second_digit_list.append(digit * 2)
        else:
            doubled_second_digit_list.append(digit)

    # add the digits if any number is more than 9
    doubled_second_digit_list = [sum_digits(x) for x in doubled_second_digit_list]
    # sum all digits
    sum_of_digits = sum(doubled_second_digit_list)
    return sum_of_digits % 10 == 0


# credit_card_valid = "4474 2054 6736 1295"
# credit_card_invalid = "1265 157309414560"
#
# print(get_credit_card_number("pop " + credit_card_valid + " apres"))
# print(get_credit_card_number("pop " + credit_card_invalid + " apres"))
# print(get_credit_card_number("1234 1234 1234 1234"))
# print(get_credit_card_number("1- 1234 1234 1234 1234"))
# print(get_credit_card_number("1- " + credit_card_valid))
