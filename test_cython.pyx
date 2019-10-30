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

#!python
#cython: boundscheck=False, wraparound=False, nonecheck=False, language_level=3
import logging
import pickle
import time

import psutil
import ray
import torch.nn.functional as F
import torch
import numpy as np
cimport numpy as np

cdef _softmax(x, axis):
    # reduce raw values to avoid NaN during exp
    x_norm = x - x.max(axis=axis, keepdims=True)
    y = np.exp(x_norm)
    return y / y.sum(axis=axis, keepdims=True)


def viterbi_cython(feats: np.ndarray, transitions_numpy: np.ndarray, tagset_size: int, id_start: int, id_stop: int,
                  all_scores):
    cdef np.ndarray backpointers = np.empty(shape=(feats.shape[0], tagset_size), dtype=np.int_)
    cdef np.ndarray backscores = np.empty(shape=(feats.shape[0], tagset_size), dtype=np.float32)

    cdef np.ndarray init_vvars = np.expand_dims(np.repeat(-10000.0, tagset_size), 0)
    init_vvars[0][id_start] = 0
    init_vvars = init_vvars.astype(np.float32)

    cdef np.ndarray forward_var = init_vvars
    cdef np.ndarray next_tag_var
    cdef np.ndarray bptrs_t
    cdef np.ndarray viterbivars_t

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

