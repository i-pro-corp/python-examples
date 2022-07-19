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
    Try connecting to an i-PRO camera with MJPEG(Motion JPEG).
    MJPEG(Motion JPEG) で i-PRO カメラと接続します

[Details]
    Let's try first. (Method 2)
    まずはやってみる（方式２）

[Author]
    kinoshita hidetoshi (木下英俊)

[library install]
    cv2:    pip install opencv-python
'''

import cv2
import numpy as np
import urllib.request as rq


user_id     = "user-id"         # Change to match your camera setting
user_pw     = "password"        # Change to match your camera setting
host        = "192.168.0.10"    # Change to match your camera setting
winname     = "VIDEO"           # Window title
resolution  = "1920x1080"       # Resolution
framerate   =  15               # Frame rate

# URL
url = f"http://{host}/cgi-bin/nphMotionJpeg?Resolution={resolution}&Quality=Standard&Framerate={framerate}"


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


set_digest_auth(url, user_id, user_pw)
stream = rq.urlopen(url)

bytes = bytes()
while True:
    try:
        bytes += stream.read(1024)
        a = bytes.find(b'\xff\xd8')     # SOI  (Start of Image)  0xFFD8
        b = bytes.find(b'\xff\xd9')     # EOI  (End   of Image)  0xFFD9
        if a != -1 and b != -1:
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]

            # Convert binary data to ndarray type.
            img_buf = np.frombuffer(jpg, dtype=np.uint8)

            # Decode ndarray data to OpenCV format image data.
            frame = cv2.imdecode(img_buf, cv2.IMREAD_UNCHANGED)

            # Please modify the value to fit your PC screen size.
            frame2 = cv2.resize(frame, (1280, 720))

            # Display video.
            cv2.imshow(winname, frame2)
            cv2.waitKey(1)      # necessary to display the video by imshow ()

    except KeyboardInterrupt:
        # Press '[ctrl] + [c]' on the console to exit the program.
        print("KeyboardInterrupt")
        break

cv2.destroyAllWindows()
