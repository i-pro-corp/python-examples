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
    Let's add face detection using OpenCV.
    OpenCV を使って顔検知を追加してみます

[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    cv2:    pip install opencv-python

[OpenCV]
    Get the file "haarcascade_frontalface_alt2.xml" from the URL below.
    下記URLからファイル "haarcascade_frontalface_alt2.xml" を入手するしてください。
    https://github.com/opencv/opencv/tree/master/data/haarcascades
'''

import cv2

user_id     = "user-id"         # Change to match your camera setting
user_pw     = "password"        # Change to match your camera setting
host        = "192.168.0.10"    # Change to match your camera setting
winname     = "VIDEO"           # Window title
resolution  = "1920x1080"       # Resolution
framerate   =  15               # Frame rate

# URL
url = f"http://{user_id}:{user_pw}@{host}/cgi-bin/nphMotionJpeg?Resolution={resolution}&Quality=Standard&Framerate={framerate}"

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

def DetectFaces(cascade, image):
    '''
    [Abstract]
        Detect faces and return recognition result.
        顔検知して認識結果を返す
    [Param]
        cascade :       CascadeClassifier object in OpenCV format.
        image :         Image in OpenCV format.
    [Return]
        Detection result.
    '''
    # Convert to grayscale image for face detection.
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces from image.
    face_list = cascade.detectMultiScale(img_gray, minSize=(100, 100))

    # Return result.
    return face_list


def DrawFaceRectangles(image, face_list):
    '''
    [Abstract]
        Draw red frames on the image according to the detection result face_list.
        検出結果 face_list にしたがって、image 上に赤枠を描画する。
    [Param]
        image :         Image in OpenCV format.
        face_list :     List of detected face frames.
    [Return]
        None
    '''
    # Draw red frames for the number of detected faces.
    if len(face_list) != 0:
        for (pos_x, pos_y, w, h) in face_list:
            print(f"pos_x = {pos_x}, pos_y = {pos_y}, w = {w}, h = {h}")
            cv2.rectangle(image, (pos_x, pos_y), (pos_x + w, pos_y + h), (0,0,255), thickness=5)


'''
[Abstract]
    main 関数
'''
if __name__ == '__main__':

    cap = cv2.VideoCapture(url)

    #
    windowInitialized = False

    # haarcascade file for opencv cascade classification.
    cascade_file = "haarcascade_frontalface_alt2.xml"       # face
    #cascade_file = "haarcascade_eye.xml"                   # eye ?
    #cascade_file = "haarcascade_eye_tree_eyeglasses.xml"   # eye ?
    cascade = cv2.CascadeClassifier(cascade_file)

    while True:
        try:
            ret, frame = cap.read()
            if ret == True:
                # 顔検知
                face_list = DetectFaces(cascade, frame)

                # 検出した顔枠を描画
                DrawFaceRectangles(frame, face_list)

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
