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
from argparse import Namespace, ArgumentParser


def train_parse_args(train: bool) -> Namespace:
    """
    Parse command line arguments.

    :returns: a namespace with all the set parameters
    """

    parser = ArgumentParser(
        description='Annotate a sample of the given files in the input directory'
    )
    parser.add_argument(
        '-m', '--model-dir',
        help="Model directory",
        action="store",
        dest="model_dir",
        required=False
    )
    parser.add_argument(
        '-i', '--input-files-dir',
        help="Input files directory",
        action="store",
        dest="input_dir",
        required=True
    )
    parser.add_argument(
        '-s', '--dev-set-size',
        help="Size of dev set",
        action="store",
        dest="dev_size",
        required=True
    )
    parser.add_argument(
        '-o', '--output-model-dir',
        help="Directory where to save model",
        action="store",
        dest="output_model_dir",
        required=False
    )

    if train:
        parser.add_argument(
            '-e', '--epochs',
            help="Number of epochs",
            action="store",
            dest="epoch",
            required=True
        )

    return parser.parse_args()
