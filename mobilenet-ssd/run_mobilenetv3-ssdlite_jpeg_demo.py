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
    Create a python program that detects objects in JPEG images using the trained AI model of "MobileNetV3 SSD-Lite".

    "MobileNetV3 SSD-Lite" の学習済みAIモデルを使用して、JPEG画像を対象に物体検知する Python プログラムを作成します。

[Details]
    This program uses pytorch "ssdlite320_mobilenet_v3_large" and pre-trained model.
    The program detects 91 classes because the trained model is trained using the COCO dataset.
    When you run this program for the first time, you will have to wait a lot of time to start the program, as it downloads the trained model.

    このプログラムは pytorch の "ssdlite320_mobilenet_v3_large" および 学習済みモデルを使用します。
    学習済みモデルは COCO dataset を使って学習しているので、このプログラムは91クラスを検知します。
    このプログラムを始めて実行するとき、このプログラムは学習済みモデルのダウンロードを行うため、あなたはプログラム起動に多くの時間を待つ必要があるでしょう。

[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    cv2:        pip install opencv-python
    pytorch:    pip install torch torchvision torchaudio

[Reference URL]
    https://pytorch.org/vision/main/models.html#object-detection
    https://pytorch.org/vision/0.11/auto_examples/plot_visualization_utils.html#visualizing-bounding-boxes

'''

from pathlib import Path
from torchvision.io.image import read_image
from torchvision.models.detection import ssdlite320_mobilenet_v3_large, SSDLite320_MobileNet_V3_Large_Weights
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image

img = read_image(str(Path('assets') / 'dog1.jpg'))

# Step 1: Initialize model with the best available weights
weights = SSDLite320_MobileNet_V3_Large_Weights.DEFAULT
model = ssdlite320_mobilenet_v3_large(weights=weights)
model = model.eval()

# Step 2: Initialize the inference transforms
preprocess = weights.transforms()

# Step 3: Apply inference preprocessing transforms
batch = [preprocess(img)]

# Step 4: Use the model and visualize the prediction
prediction = model(batch)[0]
score_threshold = 0.5
labels = [weights.meta["categories"][class_index] + f": {score_int:.2f}" for class_index, score_int in zip(prediction["labels"], prediction["scores"]) if score_int > score_threshold]
boxes = prediction["boxes"][prediction["scores"] > score_threshold]
box = draw_bounding_boxes(img, boxes=boxes,
                          labels=labels,
                          colors="red",
                          width=4,
                          font='arial.ttf', font_size=30)
im = to_pil_image(box.detach())
im.show()
