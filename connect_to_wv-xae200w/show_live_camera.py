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
    This program connects to an i-PRO camera and draws the recognition result 
    of AI-VMD (WV-XAE200WUX) on the live video.
    i-PRO カメラと接続して、AI-VMD (WV-XAE200WUX) の認識結果を受信したライブ映像に描画します。

[Details]
    This program has been confirmed to work with WV-XAE200WUX Ver. 2.20.

[Author]
    kinoshita hidetoshi (木下英俊)

[library install]
    cv2:    pip install opencv-python
    numpy:  pip install numpy
'''

import cv2
import numpy as np
import urllib.request as rq
import urllib.error
from parse_jpeg import ParseJpegFile
from draw_aivmd_rect import DrawAivmdRect


user_id     = "user-id"         # Change to match your camera setting
user_pw     = "password"        # Change to match your camera setting
host        = "192.168.0.10"    # Change to match your camera setting
winname     = "VIDEO"           # Window title
resolution  = "1920x1080"       # Resolution
framerate   =  15               # Frame rate

# URL
url = f"http://{host}/cgi-bin/nphMotionJpeg?Resolution={resolution}&Quality=Standard&Framerate={framerate}"


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


def set_digest_auth(uri, user, passwd):
    '''
    [abstract]
        Authenticate with the IP camera.

    [params]
        uri:      CGI command for start mjpeg stream.
        user:     user-id for camera.
        passwd:   user-password for camera.
    '''
    pass_mgr = rq.HTTPPasswordMgrWithDefaultRealm()
    pass_mgr.add_password(realm=None, uri=uri, user=user, passwd=passwd)
    auth_handler = rq.HTTPDigestAuthHandler(pass_mgr)
    opener = rq.build_opener(auth_handler)
    rq.install_opener(opener)


if __name__ == "__main__":
    '''
    [abstract]
        __main__ function.

    [raises]
        None
    '''
    connection = False
    while True:
        try:
            if connection == False:
                set_digest_auth(url, user_id, user_pw)
                stream = rq.urlopen(url, timeout=10)
                data = bytes()
                connection = True

            temp = stream.read(1024)

            if len(temp) == 0:
                # Probably not properly connected to the camera.
                print("[ERROR] len(temp) == 0")
                stream.close()
                connection = False

            data += temp
            a = data.find(b'\xff\xd8')     # SOI  (Start of Image)  0xFFD8
            b = data.find(b'\xff\xd9')     # EOI  (End   of Image)  0xFFD9
            if a != -1 and b != -1:
                jpg = data[a:b+2]
                data = data[b+2:]

                # Convert binary data to ndarray type.
                img_buf = np.frombuffer(jpg, dtype=np.uint8)

                # Decode ndarray data to OpenCV format image data.
                frame = cv2.imdecode(img_buf, cv2.IMREAD_UNCHANGED)

                # Extracts the recognition result of WV-XAE200WUX (AI-VMD) from the JPEG file.
                result, aivmd_result = ParseJpegFile(jpg)

                if result==True:
                    # Draws the recognition result on the received video.
                    frame = DrawAivmdRect(frame, aivmd_result)

                # Please modify the value to fit your PC screen size.
                frame2 = cv2.resize(frame, (1280, 720))

                # Display video.
                cv2.imshow(winname, frame2)

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

        except TimeoutError:
            print("[ERROR] TimeoutError happen.")
            if connection == True:
                stream.close()
                connection = False

        except urllib.error.URLError:
            print("[ERROR] URLError happen.")
            if connection == True:
                stream.close()
                connection = False

    cv2.destroyAllWindows()
