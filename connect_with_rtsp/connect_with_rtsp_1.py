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
    Let's try first.
    まずはやってみる

[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    cv2:    pip install opencv-python
'''

import cv2

user_id     = "user-id"         # Change to match your camera setting
user_pw     = "password"        # Change to match your camera setting
host        = "192.168.0.10"    # Change to match your camera setting
winname     = "VIDEO"           # Window title

cap = cv2.VideoCapture(f"rtsp://{user_id}:{user_pw}@{host}/MediaInput/stream_1")


while True:
    try:
        ret, frame = cap.read()
        if ret == True:
            # Please modify the value to fit your PC screen size.
            frame2 = cv2.resize(frame, (1280, 720))
            
            # Display video.
            cv2.imshow(winname, frame2)

        cv2.waitKey(1)      # necessary to display the video by imshow ()

    except KeyboardInterrupt:
        # Press '[ctrl] + [c]' on the console to exit the program.
        print("KeyboardInterrupt")
        break

cap.release()
cv2.destroyAllWindows()