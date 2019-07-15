#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

from match_text_unsafe.match_acora import AcoraMatcher
from match_text.match_address import find_address_in_block_of_paragraphs
from misc.normalize_offset import normalize_offsets

from spacy.tokens.doc import Doc  # type: ignore

from typing import List, Dict

import logging

logger = logging.getLogger(__name__)


def complete_case_annotations(spacy_docs: List[Doc], entity_typename: Dict[str, str]) -> List[Doc]:
    """
    Complete/Normalize annotations from the spacy tagger.

    :param spacy_docs: the spacy annotations
    :param entity_typename: the dictionary with each occurence type
    :returns: the updated spacy_annotions (for convenience only, as the update is inplace)
    """

    if len(spacy_docs) > 0:
        matcher = AcoraMatcher(content=list(entity_typename.keys()),
                               ignore_case=True)

        doc_text, empty_offsets = zip(*[(spacy_doc.text, []) for spacy_doc in spacy_docs])
        document_addresses_offsets = find_address_in_block_of_paragraphs(texts=list(doc_text),
                                                                         offsets=list(empty_offsets))

        for spacy_doc, doc_address_offset in zip(spacy_docs, document_addresses_offsets):
            matches = matcher.get_matches(text=spacy_doc.text, tag="UNKNOWN")
            matcher_offsets = list()
            for offset in matches:
                span_text = spacy_doc.text[offset.start:offset.end]
                logger.debug(span_text)
                offset.type = entity_typename[span_text.lower()]
                matcher_offsets.append(offset)
            matcher_offsets_normalized = normalize_offsets(offsets=matcher_offsets + doc_address_offset)

            spacy_matcher_offset = list()
            for offset in matcher_offsets_normalized:
                # https://spacy.io/usage/linguistic-features#section-named-entities
                span_doc = spacy_doc.char_span(offset.start, offset.end, label=offset.type)
                if span_doc is not None:
                    # span will be none if the word is incomplete
                    spacy_matcher_offset.append(span_doc)
                else:
                    logger.error(f"ERROR char offset [{spacy_doc.text[offset.start:offset.end]}] "
                                 f"from [{spacy_doc.text}]")

            spacy_doc.ents = spacy_matcher_offset  # all_offsets

    return spacy_docs
