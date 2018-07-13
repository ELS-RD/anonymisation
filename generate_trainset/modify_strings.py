from random import randint

import regex

# some organization prefix patterns
org_types = r"société(s)?|" \
            r"association|" \
            r"s(\.|\s)*a(\.|\s)*s(\.|\s)*u(\.|\s)*|" \
            r"e(\.|\s)*u(\.|\s)*rl(\.|\s)*|" \
            r"s(\.|\s)*c(\.|\s)*s|" \
            r"s(\.|\s)*n(\.|\s)*c|" \
            r"s(\.|\s)*e(\.|\s)*m|" \
            r"s(\.|\s)*c(\.|\s)*p(\.|\s)*|" \
            r"s(\.|\s)*a(\.|\s)*s|" \
            r"s(\.|\s)*a(\.|\s)*|" \
            r"s(\.|\s)*a(\.|\s)*s(\.|\s)*u(\.|\s)*|" \
            r"s(\.|\s)*a(\.|\s)*r(\.|\s)*l|" \
            r"s(\.|\s)*e(\.|\s)*l(\.|\s)*a(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            r"s(\.|\s)*c(\.|\s)*i(\.|\s)*|" \
            r"s(\.|\s)*c(\.|\s)*o(\.|\s)*p(\.|\s)*|" \
            r"s(\.|\s)*e(\.|\s)*l(\.|\s)*|" \
            r"s(\.|\s)*c(\.|\s)*a(\.|\s)*|" \
            r"e(\.|\s)*i(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            r"syndic|" \
            r"syndicat|" \
            r"(e|é)tablissement|" \
            r"mutuelle|" \
            r"caisse|" \
            r"hôpital"


def get_title_case(original_text: str) -> str:
    """
    Upper case each first letter of a MWE
    :param original_text: original full name
    :return: transformed string
    """
    return ' '.join([word.capitalize() for word in original_text.split(' ')])


def random_case_change(text: str, offsets: list, rate: int) -> str:
    """
    Randomly change the case of the string inside the offset to make the NER more robust
    :param text: original text
    :param offsets: original offsets
    :param rate: the percentage of offset to change (as integer)
    :return: the updated text
    """
    for offset in offsets:
        if randint(0, 99) <= rate:
            extracted_content = text[offset[0]:offset[1]]

            random_transformation = randint(1, 3)
            if random_transformation == 1:
                new_text = extracted_content.lower()
            elif random_transformation == 2:
                new_text = extracted_content.upper()
            else:
                new_text = get_title_case(extracted_content)

            text = text[:offset[0]] + new_text + text[offset[1]:]

    return text


remove_corp_pattern = regex.compile(r"\b(" + org_types + r")\b\s+",
                                    flags=regex.IGNORECASE)


def remove_corp(original_text: str) -> str:
    """
    Remove corporation type name
    :param original_text: Name of company included its type
    :return: the cleaned string
    """
    return remove_corp_pattern.sub(repl="", string=original_text).strip()


last_name_pattern = regex.compile(r"[A-Z\s]+$")


def get_last_name(text: str) -> str:
    """
    Extract last name from a full name
    :param text: full name
    :return: family name
    """
    result = last_name_pattern.search(text.strip())
    if result:
        return str(result.group(0)).strip()
    return ""


def get_first_last_name(text: str):
    """
    Extract first name and last name from a full name
    :param text: full name text
    :return: a tuple of string (first_name, last_name)
    """
    clean_text = text.strip()
    last_name = get_last_name(clean_text)
    first_name = clean_text[0:len(clean_text) - len(last_name)].strip() if len(last_name) > 0 else ""
    return first_name, last_name
