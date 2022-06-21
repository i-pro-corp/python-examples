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
    This program connects to an i-PRO camera and classifies live images.
    このプログラムは、i-PRO カメラと接続してライブ映像に対して画像分類を行います。

[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    torch, torchvision : see https://pytorch.org/get-started/locally/
    cv2 :           pip install opencv-python
    matplotlib :    pip install matplotlib
    numpy :         pip install numpy
    PIL :           pip install pillow
    json :          Built-in module in Python, you don’t need to install it with pip.
'''

import cv2
from PIL import Image
from classification_vgg import ImagenetClassificationVgg    # Local module. See 'classification_vgg.py'.


user_id     = "user-id"         # Change to match your camera setting
user_pw     = "password"        # Change to match your camera setting
host        = "192.168.0.10"    # Change to match your camera setting
winname     = "VIDEO"           # Window title


# Exception 定義
BackendError = type('BackendError', (Exception,), {})

def IsWindowVisible(winname):
    '''
    Check if the target window exists.

    Args:
        winname :       Window title.
    Returns:
        True :          Exist.
        False :         Not exist.
    Raise:
        BackendError :
    '''
    try:
        ret = cv2.getWindowProperty(winname, cv2.WND_PROP_VISIBLE)
        if ret == -1:
            raise BackendError('Use Qt as backend to check whether window is visible or not.')

        return bool(ret)

    except cv2.error:
        return False




def CV2Pil(image):
    '''
    Convert from OpenCV to PIL.Image
    
    Params:
        image:  OpenCV image.
    Returns:
        PIL.Image format image.    
    '''
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image


'''
[Abstract]
    main 関数
'''
if __name__ == '__main__':
    # Create an instance of class ImagenetClassificationVgg.
    imagenetClassifigationVgg = ImagenetClassificationVgg('./data/imagenet_class_index.json')

    # Create an instance of class cv2.VideoCapture
    cap = cv2.VideoCapture(f"rtsp://{user_id}:{user_pw}@{host}/MediaInput/stream_1")

    # 
    windowInitialized = False

    while True:
        try:
            ret, frame = cap.read()
            if ret == True:
                # Image classification
                pilImage = CV2Pil(frame)
                result, score = imagenetClassifigationVgg.do_classification(pilImage)

                if score > 0.15:
                    print(result, score)
                else:
                    print('None')

                # Resize to a display size that fits on your PC screen.
                width   = 640
                height  = 480
                h, w = frame.shape[:2]
                aspect = w / h
                if width / height >= aspect:
                    nh = height
                    nw = round(nh * aspect)
                else:
                    nw = width
                    nh = round(nw / aspect)
                frame2 = cv2.resize(frame, (nw, nh))
            
                # Display image.
                cv2.imshow(winname, frame2)

                if windowInitialized==False:
                    # Specify the display position only at the beginning.
                    cv2.moveWindow(winname, 100, 100)
                    windowInitialized = True

            # Press the "q" key to finish.
            k = cv2.waitKey(1) & 0xff   # necessary to display the video by imshow ()
            if k == ord("q"):
                break
            
            # Exit if there is no specified window.
            if not IsWindowVisible(winname):
                break

        except KeyboardInterrupt:
            # Press ctrl -c on the console to exit the program.
            print("KeyboardInterrupt")
            break

    print("Finish main()")
    cap.release()
    cv2.destroyAllWindows()
