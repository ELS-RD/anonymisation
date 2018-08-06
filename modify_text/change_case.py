from random import randint


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

            random_transformation = randint(1, 4)
            if random_transformation == 1:
                new_text = extracted_content.lower()
            elif random_transformation == 2:
                new_text = extracted_content.upper()
            elif random_transformation == 3:
                new_text = change_random_word_case(extracted_content)
            else:
                new_text = get_title_case(extracted_content)

            text = text[:offset[0]] + new_text + text[offset[1]:]

    return text


def change_random_word_case(text: str) -> str:
    """
    Change randomly the case of some words from the original text (lower, upper, capitalize, or do nothing).
    Applied only if the entity is made of several words.
    :param text: original text
    :return: transformed case text
    """
    words = text.split(' ')
    if len(words) == 1:
        return text
    result = list()
    for word in words:
        choice = randint(1, 4)
        if choice == 1:
            result.append(word.capitalize())
        elif choice == 2:
            result.append(word.lower())
        elif choice == 3:
            result.append(word.upper())
        else:
            result.append(word)
    return ' '.join(result)
