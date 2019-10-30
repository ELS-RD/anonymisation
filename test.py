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
import logging
import pickle
import time

import psutil
import ray
import torch.nn.functional as F
import torch
import numpy as np
import pyximport
pyximport.install()

torch.set_num_threads(1)


def read(path):
    with open(path, "rb") as f:
        return pickle.load(f)


transitions = read("transitions.pickle")
tagset_size = read("tagset_size.pickle")
tag_dictionary = read("tag_dictionary.pickle")
feature = read("feature.pickle")
lengths = read("lengths.pickle")

START_TAG: str = "<START>"
STOP_TAG: str = "<STOP>"

# def _viterbi_decode(feats, transitions, tagset_size, tag_dictionary, all_scores: bool = False):
#     backpointers = []
#     backscores = []
#
#     init_vvars = torch.FloatTensor(1, tagset_size).fill_(-10000.0)
#     init_vvars[0][tag_dictionary.get_idx_for_item(START_TAG)] = 0
#     forward_var = init_vvars
#     for feat in feats:
#         next_tag_var = (
#                 forward_var.view(1, -1).expand(tagset_size, tagset_size)
#                 + transitions
#         )
#         _, bptrs_t = torch.max(next_tag_var, dim=1)
#         viterbivars_t = next_tag_var[range(len(bptrs_t)), bptrs_t]
#         forward_var = viterbivars_t + feat
#         backscores.append(forward_var)
#         backpointers.append(bptrs_t)
#     terminal_var = (
#             forward_var + transitions[tag_dictionary.get_idx_for_item(STOP_TAG)]
#     )
#     terminal_var.detach()[tag_dictionary.get_idx_for_item(STOP_TAG)] = -10000.0
#     terminal_var.detach()[
#         tag_dictionary.get_idx_for_item(START_TAG)
#     ] = -10000.0
#     best_tag_id = torch.argmax(terminal_var.unsqueeze(0))
#
#     best_path = [best_tag_id]
#     for bptrs_t in reversed(backpointers):
#         best_tag_id = bptrs_t[best_tag_id]
#         best_path.append(best_tag_id)
#
#     best_scores = []
#     for backscore in backscores:
#         softmax = F.softmax(backscore, dim=0)
#         _, idx = torch.max(backscore, 0)
#         prediction = idx.item()
#         best_scores.append(softmax[prediction].item())
#
#     start = best_path.pop()
#     assert start == tag_dictionary.get_idx_for_item(START_TAG)
#     best_path.reverse()
#     scores = []
#     # return all scores if so selected
#     if all_scores:
#         for backscore in backscores:
#             softmax = F.softmax(backscore, dim=0)
#             scores.append([elem.item() for elem in softmax.flatten()])
#
#         for index, (tag_id, tag_scores) in enumerate(zip(best_path, scores)):
#             if type(tag_id) != int and tag_id.item() != np.argmax(tag_scores):
#                 swap_index_score = np.argmax(tag_scores)
#                 scores[index][tag_id.item()], scores[index][swap_index_score] = (
#                     scores[index][swap_index_score],
#                     scores[index][tag_id.item()],
#                 )
#             elif type(tag_id) == int and tag_id != np.argmax(tag_scores):
#                 swap_index_score = np.argmax(tag_scores)
#                 scores[index][tag_id], scores[index][swap_index_score] = (
#                     scores[index][swap_index_score],
#                     scores[index][tag_id],
#                 )
#
#     return best_scores, best_path, scores
#
#
# s = time.time()
# for feats, length in zip(feature, lengths):
#     t1 = _viterbi_decode(feats[:length], transitions, tagset_size, tag_dictionary, True)
#     # print(t)
# print(time.time() - s)


from test_cython import viterbi_cython


def chunks(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        s = seq[int(last):int(last + avg)]
        indexes = list(range(len(s)))
        out.append((indexes, s))
        last += avg

    return out


def _softmax(x, axis):
    # reduce raw values to avoid NaN during exp
    x_norm = x - x.max(axis=axis, keepdims=True)
    y = np.exp(x_norm)
    return y / y.sum(axis=axis, keepdims=True)


def viterbi_numpy(feats: np.ndarray, transitions_numpy: np.ndarray, tagset_size: int, id_start: int, id_stop: int,
                  all_scores):
    backpointers = np.empty(shape=(feats.shape[0], tagset_size), dtype=np.int_)
    backscores = np.empty(shape=(feats.shape[0], tagset_size), dtype=np.float32)

    init_vvars = np.expand_dims(np.repeat(-10000.0, tagset_size), 0)
    init_vvars[0][id_start] = 0
    init_vvars = init_vvars.astype(np.float32)

    forward_var = init_vvars
    for index, feat in enumerate(feats):
        next_tag_var = forward_var + transitions_numpy
        bptrs_t = np.argmax(next_tag_var, axis=1)
        viterbivars_t = next_tag_var[np.arange(bptrs_t.shape[0]), bptrs_t]
        forward_var = viterbivars_t + feat
        backscores[index] = forward_var
        forward_var = forward_var[np.newaxis, :]
        backpointers[index] = bptrs_t

    terminal_var = forward_var.squeeze() + transitions_numpy[id_stop]
    terminal_var[id_stop] = -10000.0
    terminal_var[id_start] = -10000.0
    best_tag_id = np.argmax(terminal_var)

    best_path = [best_tag_id]
    for bptrs_t in np.flip(backpointers, 0):
        best_tag_id = bptrs_t[best_tag_id]
        best_path.append(best_tag_id)
    start = best_path.pop()
    assert start == id_start
    best_path.reverse()

    best_scores_softmax = _softmax(backscores, axis=1)
    best_scores_np = np.max(best_scores_softmax, axis=1)

    all_scores_np = np.empty(0)
    # return all scores if so selected
    if all_scores:
        all_scores_np = best_scores_softmax

        for index, (tag_id, tag_scores) in enumerate(zip(best_path, all_scores_np)):
            if type(tag_id) != int and tag_id.item() != np.argmax(tag_scores):
                swap_index_score = np.argmax(tag_scores)
                all_scores_np[index][tag_id.item()], all_scores_np[index][swap_index_score] = (
                    all_scores_np[index][swap_index_score],
                    all_scores_np[index][tag_id.item()],
                )
            elif type(tag_id) == int and tag_id != np.argmax(tag_scores):
                swap_index_score = np.argmax(tag_scores)
                all_scores_np[index][tag_id], all_scores_np[index][swap_index_score] = (
                    all_scores_np[index][swap_index_score],
                    all_scores_np[index][tag_id],
                )

    return best_scores_np, best_path, all_scores_np


@ray.remote
def viterbi_ray_batch(feature_numpy: np.ndarray, indexes, lengths, transitions_numpy: np.ndarray, tagset_size: int,
                      id_start: int, id_stop: int,
                      all_scores):
    results = list()
    for index, length in zip(indexes, lengths):
        feats = feature_numpy[index][: length]
        r = viterbi_numpy(feats=feats,
                          transitions_numpy=transitions_numpy,
                          tagset_size=tagset_size,
                          id_start=id_start,
                          id_stop=id_stop,
                          all_scores=all_scores)
        results.append(r)

    return results


num_cpus = psutil.cpu_count(logical=False)
ray.init(num_cpus=num_cpus, num_gpus=0, logging_level=logging.ERROR)

transitions_numpy = transitions.numpy()
id_start = tag_dictionary.get_idx_for_item(START_TAG)
id_stop = tag_dictionary.get_idx_for_item(STOP_TAG)
init_vvars = np.expand_dims(np.repeat(-10000.0, tagset_size), 0)
init_vvars[0][id_start] = 0

transitions_numpy_id = ray.put(transitions_numpy)
s = time.time()
for _ in range(20):
    tasks = list()
    feature_numpy = feature.numpy()
    feature_numpy_id = ray.put(feature_numpy)

    for indexes, l in chunks(lengths, 6):
        task = viterbi_ray_batch.remote(feature_numpy_id, indexes, l, transitions_numpy_id, tagset_size, id_start, id_stop,
                                        False)
        tasks.append(task)
    _ = ray.get(tasks)
print((time.time() - s) / 20)


ray.shutdown()




s = time.time()
for _ in range(20):
    tasks = list()
    feature_numpy = feature.numpy()
    for i in range(feature_numpy.shape[0]):
        _ = viterbi_cython(feature_numpy[1], transitions_numpy, tagset_size, id_start, id_stop, False)

print((time.time() - s) / 20)



s = time.time()
for _ in range(20):
    tasks = list()
    feature_numpy = feature.numpy()
    for i in range(feature_numpy.shape[0]):
        _ = viterbi_numpy(feature_numpy[1], transitions_numpy, tagset_size, id_start, id_stop, False)

print((time.time() - s) / 20)




# s_time = time.time()
# feature_np = feature.numpy()
# for index, length in enumerate(lengths):
#     feature_np[index, length:] = 0  # TODO replace 0 by dict
# softmax = _softmax(feature_np, axis=2)
# prediction = feature_np.argmax(axis=2)
# scores = feature_np.max(axis=2)
# for s_max, p, s, l in zip(softmax, prediction, scores, lengths):
#     tag_seq_ = p[:l].tolist()
#     confidences_ = s[:l].tolist()
#     scores_ = s_max[tag_seq_].tolist()
#
# print(time.time() - s_time)


# s = time.time()
# feature_copy = feature.detach().cpu()
# for index, length in chunks(lengths, 6):
#     feature_copy[index, length:] = 0  # TODO replace 0 by dict
#
# softmax_batch = F.softmax(feature_copy, dim=2).cpu()
# scores_batch, prediction_batch = torch.max(softmax_batch, 2)
#
# for softmax, score, prediction, length in zip(softmax_batch, scores_batch, prediction_batch, lengths):
#     tag_seq_ = prediction[:length].tolist()
#     confidences_ = score[:length].tolist()
#     scores_ = softmax[:length].tolist()
#
# print(time.time() - s)
#
# s = time.time()
# for feats, length in zip(feature, lengths):
#     tag_seq = []
#     confidences = []
#     scores = []
#     for backscore in feats[:length]:
#         softmax = F.softmax(backscore, dim=0)
#         _, idx = torch.max(backscore, 0)
#         prediction = idx.item()
#         tag_seq.append(prediction)
#         confidences.append(softmax[prediction].item())
#         scores.append(softmax.tolist())
# print(time.time() - s)
