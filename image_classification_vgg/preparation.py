'''
Copyright 2022 i-PRO Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

'''
[Abstract]
    Image classification.
    画像分類を行います。

[Details]
    This program prepares for image classification.
    このプログラムを動作させることで、画像分類を行うための事前準備を行います。

[Author]
    kinoshita hidetoshi (木下英俊)
'''

import os
import urllib.request

# Create the folder "data" when the folder "data" does not exist. 
# フォルダ「data」が存在しない場合はフォルダ data を作成します。
data_dir = "./data/"
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

# Download class_index for ImageNet.
# It is prepared for Keras. This is the JSON file used by the following open source.
# ImageNetのclass_indexをダウンロードします。
# Kerasで用意されているものです。下記オープンソースで使用している JSON ファイルです。
# https://github.com/fchollet/deep-learning-models/blob/master/imagenet_utils.py
url = "https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json"
save_path = os.path.join(data_dir, "imagenet_class_index.json")

if not os.path.exists(save_path):
    urllib.request.urlretrieve(url, save_path)
