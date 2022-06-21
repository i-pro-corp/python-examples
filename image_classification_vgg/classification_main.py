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
    Easy sample of image classification of still images (JPEG files) using 'classification_vgg.py'.
    'classification_vgg.py' を使って静止画(JPEG files)の画像分類を簡単に実現します。

[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    PIL :           pip install pillow

[Note]
    The 'classification_vgg.py' file must be saved in the same folder as this source code.
    Download the JPEG file yourself and save it in the data folder. See main function.

    'classification_vgg.py' ファイルをこのソースコードと同じフォルダに保存してある必要があります。
    JPEGファイルはご自身でダウンロードして data フォルダに保存を行ってください。main 関数内の記載をご確認ください。
'''

from PIL import Image
from classification_vgg import ImagenetClassificationVgg    # Local module. See 'classification_vgg.py'.

if __name__ == "__main__":
    '''
    main
    '''
    imagenetClassifigationVgg = ImagenetClassificationVgg('./data/imagenet_class_index.json')

    # Open image file.
    # https://pixabay.com/ja/photos/%e3%81%a6%e3%82%93%e3%81%a8%e3%81%86%e8%99%ab-%e7%94%b2%e8%99%ab-%e3%83%86%e3%83%b3%e3%83%88%e3%82%a6%e3%83%a0%e3%82%b7-1480102/
    # https://pixabay.com/ja/service/license/
    # 商用利用無料、帰属表示必要なし、1280x855
    img = Image.open('./data/ladybug-g7744c038e_1280.jpg')
    result = imagenetClassifigationVgg.do_classification(img)
    print("Result: ", result)
