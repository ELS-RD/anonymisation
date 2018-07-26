import pickle
import warnings

import acora

from generate_trainset.match_acora import get_acora_object
from ner.model_factory import token_types
from resources.config_provider import get_config_default

config_training = get_config_default()
training_set_export_path = config_training["training_set"]


def get_frequent_entities(path_trainset: str, threshold_occurrences: int) -> dict():
    """
    Analyze recognized entities and return those over a defined threshold in a dict entity -> type_name
    :param path_trainset: path to a file storing the entity
    :param threshold_occurrences: minimum number of occurences of the entity
    :return:
    """
    try:
        with open(path_trainset, 'rb') as f:
            data = pickle.load(file=f)

        def get_default_dict_value() -> dict:
            default_dict_value = dict([(token, set()) for token in token_types])
            # default_dict_value['general_count'] = 0
            return default_dict_value

        exhaustive_dict = dict()

        for case_id, text, entities in data:
            for start_offset, end_offset, type_name in entities['entities']:
                entity_span = text[start_offset:end_offset].lower()
                current_count = exhaustive_dict.get(entity_span, get_default_dict_value())
                current_count[type_name].add(case_id)
                exhaustive_dict[entity_span] = current_count

        final_list = list()

        for entity_span, dict_counts in exhaustive_dict.items():

            max_count = 0
            max_type_name = None
            for type_name, case_ids in dict_counts.items():
                current_count = len(case_ids)
                if current_count > max_count:
                    max_type_name = type_name
                    max_count = current_count

            if (max_count > threshold_occurrences) and \
                    (len(entity_span) > 3) \
                    and (max_type_name != "PARTIE_PP"):
                final_list.append((entity_span, max_type_name))

        return dict(final_list)

    except:
        warnings.warn("Empty dict of frequent entities", Warning)
        return dict()


def get_frequent_entities_matcher(content: dict) -> acora._cacora.UnicodeAcora:
    """
    Build an Acora matcher based on the dict of frequent entities
    :param content: dict of entities
    :return: an Acora matcher matcher
    """
    if len(content) > 0:
        return get_acora_object(content=list(content.keys()),
                                ignore_case=True)
    else:
        return get_acora_object(content=["!@#$%^&*()"],
                                ignore_case=True)


def get_frequent_entities_matches(matcher: acora._cacora.UnicodeAcora, frequent_entities_dict: dict, text: str) -> list:
    """
    Find matches of frequent entities in the provided text
    :param matcher: an acora matcher based on the frequent entities
    :param frequent_entities_dict:
    :param text: original text
    :return: a list of offsets
    """
    match_results = matcher.findall(text)
    entities = list()
    for match_text, start_offset in match_results:
        end_offset = start_offset + len(match_text)
        entity_span = text[start_offset:end_offset]

        # end_offset is one character after the end of the selection,
        # so it can be equal to the last charcter offset of the text + 1
        last_char_ok = (end_offset == len(text)) or (not text[end_offset].isalnum())

        first_char_ok = (start_offset == 0 or not text[start_offset - 1].isalnum()) and \
                        (text[start_offset].isupper() or text[start_offset].isdecimal())

        if first_char_ok and last_char_ok:
            type_name = frequent_entities_dict[entity_span.lower()]
            entities.append((start_offset, end_offset, type_name))

    return entities
