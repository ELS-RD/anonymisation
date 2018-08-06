from spacy.tokens.doc import Doc

from ner.model_factory import token_types


class EntityTypename:
    __entity_count_type_dict = dict()
    __entity_type_dict = dict()

    @staticmethod
    def __get_default_dict_value() -> dict:
        """
        Build a new 0 count dict for each type of token
        :return: 0 count dict
        """
        default_dict_value = dict([(token, 0) for token in token_types])
        return default_dict_value

    def add_spacy_entities(self, spacy_doc: Doc):
        """
        Retrieve entities extracted from a Spacy doc and count each type taken by each entity.
        :param spacy_doc: original doc parsed by Spacy
        """
        for ent in spacy_doc.ents:
            entity_text = ent.text.lower()
            entity_label = ent.label_
            current_count = self.__entity_count_type_dict.get(entity_text, self.__get_default_dict_value())
            current_count[entity_label] += 1
            self.__entity_count_type_dict[entity_text] = current_count

    def get_dict(self):
        """
        Build a dict for each entity, and link it to the most recurrent typename
        :return: a dict (entity text -> type name)
        """
        if len(self.__entity_type_dict) > 0:
            return self.__entity_type_dict
        else:
            for entitity_text, count_dict in self.__entity_count_type_dict.items():
                max_typename_text = None
                max_typename_count = 0
                for type_name_text, count_type_name in count_dict.items():
                    if count_type_name > max_typename_count:
                        max_typename_count = count_type_name
                        max_typename_text = type_name_text
                self.__entity_type_dict[entitity_text] = max_typename_text
            return self.__entity_type_dict

    def clear(self):
        """
        Reset the entities and their counts
        """
        self.__entity_count_type_dict = dict()
        self.__entity_type_dict = dict()
