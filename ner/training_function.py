import random
from pathlib import Path
import spacy
from spacy import util
from tqdm import tqdm

token_types = ["PARTIE_PP", "PARTIE_PM", "AVOCAT", "PRESIDENT", "CONSEILLER", "GREFFIER", "ADRESSE"]


def train_model(data: list, folder_to_save_model: str, n_iter: int, batch_size: int, dropout_rate: float):
    """
    Train a NER model using Spacy
    :param data: list of tuples [(text, offset)]
    :param folder_to_save_model: Where to save the learned model. None to skip. Will be overiden with new model
    :param n_iter: number iterations of the CNN
    :param batch_size: more = less precise / less time to learn
    :param dropout_rate: more : learn less / better generalization
    """
    # Important to setup the right language because it impacts the tokenizer, sentences split, ...
    nlp = spacy.blank('fr')

    ner = nlp.create_pipe('ner')
    nlp.add_pipe(ner, last=True)

    # add labels
    for token_type in token_types:
        ner.add_label(token_type)

    optimizer = nlp.begin_training()
    with tqdm(total=n_iter * len(data) / batch_size) as pbar:
        for itn in range(n_iter):
            print("\nIter", itn + 1)
            losses = {}
            random.shuffle(data)
            batches = util.minibatch(data, batch_size)

            for current_batch_item in batches:
                texts, annotations = zip(*current_batch_item)
                # current_case_id, texts, _, annotations = zip(*current_batch_item)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=dropout_rate,  # dropout - make it harder to memorise resources
                    sgd=optimizer,  # callable to update weights
                    losses=losses)
                pbar.update(1)

            print(losses)

    # save model to output directory
    if folder_to_save_model is not None:
        folder_to_save_model = Path(folder_to_save_model)
        nlp.to_disk(folder_to_save_model)
