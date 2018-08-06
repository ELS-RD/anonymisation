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

            random_transformation = randint(1, 3)
            if random_transformation == 1:
                new_text = extracted_content.lower()
            elif random_transformation == 2:
                new_text = extracted_content.upper()
            else:
                new_text = get_title_case(extracted_content)

            text = text[:offset[0]] + new_text + text[offset[1]:]

    return text

