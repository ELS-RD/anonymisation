import regex

last_name_pattern = regex.compile("[A-Z\s]+$")


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

