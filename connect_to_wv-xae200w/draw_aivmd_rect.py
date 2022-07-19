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
    This program extracts the recognition result of AI-VMD (WV-XAE200WUX) from the JPEG file,
    and the program draws the recognition result on the received image.
    AI-VMD (WV-XAE200WUX) の認識結果を JPEG ファイルから取り出し、受信した映像に認識結果を描画します。

[Details]
    This program has been confirmed to work with WV-XAE200WUX Ver. 2.20.
    
[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    cv2:    pip install opencv-python
    numpy:  pip install numpy

[Note]
    You need to save "parse_jpeg.py" in the same location as this program.
'''

import numpy as np
import cv2
from parse_jpeg import ParseJpegFile


def DrawAivmdRect(img, aivmd_result):
    '''
    This function draws recognition frames and texts on a given image according to the WV-XAE200WUX (AI-VMD) recognition result.
    WV-XAE200WUX (AI-VMD) 認識結果に従って、与えられた画像に認識枠とテキストを描画する。

    Args:
        img             [i] OpenCV image
        aivmd_result    [i] WV-XAE200WUX (aivmd) recognition result.
    Returns:
        img             Image with recognition frames and texts drawn.
    Raises
        None
    '''
    img_width  = img.shape[1]
    img_height = img.shape[0]
    aivmd_image_width = aivmd_result['imageWidth']
    aivmd_image_height = aivmd_result['imageHeight']

    # Draw rectangles and labels.
    if len(aivmd_result['detectResult']) != 0:
        for result in aivmd_result['detectResult']:
            pos_x = int(result['hstart'] * img_width  / aivmd_image_width)
            pos_y = int(result['vstart'] * img_height / aivmd_image_height)
            w     = int(result['hcnt']   * img_width  / aivmd_image_width)
            h     = int(result['vcnt']   * img_height / aivmd_image_height)
            obj   = int(result['almObj'])

            label = ''
            thickness = 3

            if obj == 1:
                # Person
                label = 'Person'
                color = (0,0,255)   # red
            if obj == 2:
                # Car
                label = 'Car'
                color = (255,0,0)   # blue
            if obj == 3:
                # Bike
                label = 'Bike'
                color = (0,255,0)   # green
            if obj == 4:
                # Future notification candidates
                label = ''
                color = (255,255,0) # sky blue
                thickness = 1

            # draw rectangles.
            cv2.rectangle(img, (pos_x, pos_y), (pos_x + w, pos_y + h), color, thickness=thickness)

            # draw text.
            label_pos_x = pos_x
            label_pos_y = pos_y - 10
            if label_pos_y <= 10:
                label_pos_y = pos_y + h + 30
            cv2.putText(img,
                text = label,
                org = (label_pos_x, label_pos_y),
                fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                fontScale = 1.0,
                color = color,
                thickness = 2,
                lineType = cv2.LINE_AA)

    return img


if __name__ == "__main__":
    '''
    __main__ function.

    Raises
        FileNotFoundError :     Make sure that there is a file to set in FileName.
    '''
    filename = 'image_000001.jpg'       # Set the file name you use for the evaluation here.

    with open(filename, 'rb') as fin:
        binaryData = fin.read()

    # Convert from binary to ndarray.
    img_buf= np.frombuffer(binaryData, dtype=np.uint8)

    # Convert from ndarray to OpenCV image.
    img = cv2.imdecode(img_buf, cv2.IMREAD_UNCHANGED)

    # Extracts the recognition result of WV-XAE200WUX (AI-VMD) from the JPEG file.
    result, aivmd_result = ParseJpegFile(binaryData)

    if result==True:
        # Draws the recognition result on the received video.
        img = DrawAivmdRect(img, aivmd_result)

    # Please modify the value to fit your PC screen size.
    resizedImage = cv2.resize(img, (1280, 720))

    # Display video.
    windowTitle = "AI-VMD detection result."
    cv2.imshow(windowTitle, resizedImage)
    cv2.moveWindow(windowTitle, 100, 30)
    cv2.waitKey(0)      # necessary to display the video by imshow()
