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
    Try connecting to an i-PRO camera with JPEG(1 shot).
    JPEG(1 shot) で i-PRO カメラと接続してみる

[Details]
    Add reconnection when video is disconnected to "connect_with_jpeg_2.py".
    "connect_with_jpeg_2.py" へ映像切断時の再接続処理を追加する。

[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    pip install opencv-python
    pip install numpy
    pip install requests
'''

import requests
from requests.auth import HTTPDigestAuth
import numpy as np
import cv2
from urllib3 import HTTPConnectionPool

user_id     = "user-id"         # Change to match your camera setting
user_pw     = "password"        # Change to match your camera setting
host        = "192.168.0.10"    # Change to match your camera setting
winname     = "VIDEO"           # Window title
resolution  = 1920              # Resolution

# URL
url = f"http://{host}/cgi-bin/camera?resolution={resolution}"

#
initialized = False

# Exception Definition
BackendError = type('BackendError', (Exception,), {})

def IsWindowVisible(winname):
    '''
    [Abstract]
        Check if the target window exists.
        対象ウィンドウが存在するかを確認する。
    [Param]
        winname :       Window title
    [Return]
        True :          exist
                        存在する
        False :         not exist
                        存在しない
    [Exception]
        BackendError :
    '''
    try:
        ret = cv2.getWindowProperty(winname, cv2.WND_PROP_VISIBLE)
        if ret == -1:
            raise BackendError('Use Qt as backend to check whether window is visible or not.')

        return bool(ret)

    except cv2.error:
        return False


while True:
    try:
        # Request and receive image from camera.
        rs = requests.get(url, auth=HTTPDigestAuth(user_id, user_pw), timeout=10)

        # Convert from binary to ndarray.
        img_buf= np.frombuffer(rs.content, dtype=np.uint8)

        # Convert from ndarray to OpenCV image.
        img1 = cv2.imdecode(img_buf, cv2.IMREAD_UNCHANGED)

        # Please modify the value to fit your PC screen size.
        img2 = cv2.resize(img1, (1280, 720))

        # Display image.
        cv2.imshow(winname, img2)

        if initialized==False:
            # Specify window position only once at startup.
            cv2.moveWindow(winname, 100, 100)
            initialized = True
            
        # Press the "q" key to finish.
        k = cv2.waitKey(1) & 0xff   # necessary to display the video by imshow ()
        if k == ord("q"):
            break

        # Exit the program if there is no specified window.
        if not IsWindowVisible(winname):
            break

    except KeyboardInterrupt:
        # Press '[ctrl] + [c]' on the console to exit the program.
        print("KeyboardInterrupt")
        break

    except requests.ConnectTimeout as e:
        # Connection timeout.
        print(e)

    except requests.exceptions.Timeout as e:
        # Read timeout.
        print(e)

    except Exception as e:
        # Other unexpected exceptions.
        print(e)

cv2.destroyAllWindows()
