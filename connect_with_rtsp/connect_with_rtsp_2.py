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
    Try connecting to an i-PRO camera with RTSP.
    RTSP で i-PRO カメラと接続してみる

[Details]
    Let's improve the three issues of "connect_with_rtsp_1.py".
    "connect_with_rtsp_1.py" で確認した下記３つの課題を改善してみます。

    [Issues 1]
    Specifies the position where the window is displayed.
    ウィンドウを指定する場所に表示するようにします。
    [Issues 2]
    Modify the program so that you can exit the program by clicking the [x] button.
    ウィンドウ右上の[x]ボタンでプログラムを終了できるようにします。
    [Issues 3]
    Modify the program so that you can exit the program by pressing the [q] key.
    "q" キー押下でプログラムを終了できるようにします。

[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    pip install opencv-python
'''

import cv2

user_id     = "user-id"         # Change to match your camera setting
user_pw     = "password"        # Change to match your camera setting
host        = "192.168.0.10"    # Change to match your camera setting
winname     = "VIDEO"           # Window title

cap = cv2.VideoCapture(f"rtsp://{user_id}:{user_pw}@{host}/MediaInput/stream_1")

#
windowInitialized = False

# Exception 定義
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
        ret, frame = cap.read()
        if ret == True:
            # Please modify the value to fit your PC screen size.
            frame2 = cv2.resize(frame, (1280, 720))
            # Display video.
            cv2.imshow(winname, frame2)

            if windowInitialized==False:
                # Specify window position only once at startup.
                cv2.moveWindow(winname, 100, 100)
                windowInitialized = True

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

cap.release()
cv2.destroyAllWindows()