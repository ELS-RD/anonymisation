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
import html
from typing import Union, List
from flair.data import Sentence

colors = {"PERS": "#ff9933",  # orange
          "PHONE_NUMBER": "#ff9933",
          "LICENCE_PLATE": "#ff9933",
          # "SOCIAL_SECURITY_NUMBER": "#ff9933",
          "ADDRESS": "#ff99cc",  # pink
          "ORGANIZATION": "#00ccff",  # blue
          "LAWYER": "#ccffcc",  # light green
          "JUDGE_CLERK": "#ccccff",  # purple
          "COURT": "#ccffff",  # light blue
          "RG": "#99ff99",  # green
          "DATE": "#ffcc99",  # salmon
          "BAR": "#ffe699",  # light yellow
          "UNKNOWN": "#ff0000"}  # red

TAGGED_ENTITY = '''
<mark class="entity" style="background: {color}; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 3; border-radius: 0.35em; box-decoration-break: clone; -webkit-box-decoration-break: clone">
    {entity}
    <span style="font-size: 0.8em; font-weight: bold; line-height: 3; border-radius: 0.35em; text-transform: uppercase; vertical-align: middle; margin-left: 0.5rem">{label}</span>
</mark>
'''

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Flair</title>
    </head>

    <body style="font-size: 16px; font-family: 'Segoe UI'; padding: 4rem 2rem">{text}</body>
</html>
"""


def split_to_spans(s: Sentence):
    orig = s.to_original_text()
    last_idx = 0
    spans = []
    tagged_ents = s.get_spans('ner')
    for ent in tagged_ents:
        if last_idx != ent.start_pos:
            spans.append((orig[last_idx:ent.start_pos], None))
        spans.append((orig[ent.start_pos:ent.end_pos], ent.tag))
        last_idx = ent.end_pos
    if last_idx < len(orig) - 1:
        spans.append((orig[last_idx:len(orig)], None))
    return spans


def render_ner_html(sentences: Union[List[Sentence], Sentence], settings=None, wrap_page=True) -> str:
    """
    :param sentences: single sentence or list of sentences to convert to HTML
    :param settings: overrides and completes default settings; includes colors and labels dictionaries
    :param wrap_page: if True method returns result of processing sentences wrapped by &lt;html&gt; and &lt;body&gt; tags, otherwise - without these tags
    :return: HTML as a string
    """
    if isinstance(sentences, Sentence):
        sentences = [sentences]

    colors = {
        "PER": "#F7FF53",
        "ORG": "#E8902E",
        "LOC": "#FF40A3",
        "MISC": "#4647EB",
        "O": "#ddd",
    }

    if settings and "colors" in settings:
        colors.update(settings["colors"])

    labels = {
        "PER": "PER",
        "ORG": "ORG",
        "LOC": "LOC",
        "MISC": "MISC",
        "O": "O",
    }

    if settings and "labels" in settings:
        labels.update(settings["labels"])

    tagged_html = []
    for s in sentences:
        spans = split_to_spans(s)

        for fragment, tag in spans:
            escaped_fragment = html.escape(fragment).replace('\n', '<br/>')
            if tag:
                escaped_fragment = TAGGED_ENTITY.format(entity=escaped_fragment,
                                                        label=labels.get(tag, "O"),
                                                        color=colors.get(tag, "#ddd"))
            tagged_html.append(escaped_fragment)

    final_text = ''.join(tagged_html)

    if wrap_page:
        return HTML_PAGE.format(text=final_text)
    else:
        return final_text