import re

remove_corp_pattern = re.compile(r"\b(sa|sarl|sas|société|association|sasu|eurl|scs|scp)\b\s+", flags=re.IGNORECASE)


def remove_corp(original_text: str) -> str:
    """
    Remove corporation type name
    :param original_text: Name of company included its type
    :return: the cleaned string
    """
    return remove_corp_pattern.sub(repl="", string=original_text).strip()


family_name_pattern = re.compile(r"[A-Z\s]+$")


def get_family_name(original_text: str) -> str:
    """
    Extract family name from a full name
    :param original_text: full name
    :return: family name
    """
    result = family_name_pattern.search(original_text.strip())
    if result:
        return str(result.group(0)).strip()
    return ""


def get_title_case(original_text: str) -> str:
    """
    Upper case each first letter of a MWE
    :param original_text: original full name
    :return: transformed string
    """
    return ' '.join([word.capitalize() for word in original_text.split(' ')])


def add_tag(l: list, tag: str) -> list:
    """
    Build a tag item tuple
    :param l: list of items
    :param tag: tag to add
    :return: a list of tuples
    """
    return [(tag, item) for item in l]


def get_list_of_items_to_search(current_header: dict) -> list:
    """
    Create variations of items to search
    :param current_header: original list from headers
    :return: expanded list of items
    """
    items_to_search = list()
    for full_content, short_content in zip(
            current_header['defendeur_fullname'] + current_header['demandeur_fullname'],
            current_header['defendeur_hidden'] + current_header['demandeur_hidden']):
        if short_content is None:
            items_to_search.append(("PARTIE_PM", full_content))
            no_corp = remove_corp(full_content)
            if no_corp != full_content:
                items_to_search.append(("PARTIE_PM", no_corp))

        else:
            family_name = get_family_name("full_content")
            items_to_search.append(("PARTIE_PP", family_name.upper()))
            items_to_search.append(("PARTIE_PP", family_name))
            items_to_search.append(("PARTIE_PP", family_name.lower()))
            items_to_search.append(("PARTIE_PP", get_title_case(family_name)))

    items_to_search.extend(add_tag(current_header['avocat'], "AVOCAT"))
    # TODO AJOUTER DES VARIATIONS SANS LE Me
    # TODO AJOUTER VARIATIONS Juste avec le nom de famille (si prenom)
    # TODO Virer Sans avocat
    items_to_search.extend(add_tag(current_header['president'], "PRESIDENT"))
    # TODO AJOUTER VARIATIONS Juste avec le nom de famille (si prenom)
    items_to_search.extend(add_tag(current_header['conseiller'], "CONSEILLER"))
    # TODO AJOUTER VARIATIONS Juste avec le nom de famille (si prenom)
    items_to_search.extend(add_tag(current_header['greffier'], "GREFFIER"))
    # TODO AJOUTER VARIATIONS Juste avec le nom de famille (si prenom)
    return items_to_search
