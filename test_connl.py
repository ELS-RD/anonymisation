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
from flair.data import Sentence
from flair.datasets import CONLL_03
from flair.models import SequenceTagger

tagger = SequenceTagger.load('ner')

corpus = CONLL_03()
sentences = corpus.get_all_sentences()
print(len(sentences))

tagger.predict(sentences=sentences,
               mini_batch_size=256,
               embedding_storage_mode="none",
               verbose=True)

# ;CUDA_LAUNCH_BLOCKING=1
# import cupy
# from torch import nn
# from torch.nn import Embedding
# from torch.utils.dlpack import to_dlpack
# from torch.utils.dlpack import from_dlpack
#
#
# class PMemory(cupy.cuda.memory.BaseMemory):
#     def __init__(self, size):
#         self.size = size
#         self.device_id = cupy.cuda.device.get_device_id()
#         self.ptr = 0
#         if size > 0:
#             self.ptr = cupy.cuda.runtime.hostAlloc(size, 0)
#
#     def __del__(self):
#         if self.ptr:
#             cupy.cuda.runtime.freeHost(self.ptr)
#
#
# class DataGadget:
#     def __init__(self, embeddings: Embedding, cpu_pin=True):
#
#         if cpu_pin:
#             cupy.cuda.set_allocator(self.pinned_allocator)
#
#         self.cupy_corpus = cupy.fromDlpack(to_dlpack(embeddings.weight))
#
#         if cpu_pin:
#             cupy.cuda.set_allocator(None)
#
#     def get(self, indexes):
#         return from_dlpack(self.cupy_corpus[indexes].toDlpack())
#
#     @staticmethod
#     def pinned_allocator(bsize):
#         return cupy.cuda.memory.MemoryPointer(PMemory(bsize), 0)
#
#
# u_embeddings = nn.Embedding(10, 10, sparse=True).float().cuda()
# u_embeddings.weight.data.uniform_(-1, 1)
#
# datagadget = DataGadget(u_embeddings, True)
# datagadget.get([1])
