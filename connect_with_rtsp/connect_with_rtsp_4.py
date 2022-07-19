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
    Save the received image as a JPEG file.
    Add a 6-digit number to the end of the file name and save it as a serial number.
    Exit the program after saving 100 files.

    プログラム起動から10秒経過後から、受信した映像を JPEG ファイル保存します。
    ファイル名の末尾に６ケタの番号を付けて連番で保存します。
    100枚 保存したらプログラムを終了します。

[Note]
    If you set a high number of frame rates or high resolution for the camera,
    the program may not save the file because the program's file saving process may not be in time.

    カメラ側の設定でフレームレート数を高くする、解像度を高くする、などした場合は
    ファイル保存の処理が追い付かなくなってバッファが満杯になり、
    ファイル保存が間引かれる場合があります。

[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    cv2:    pip install opencv-python
'''

import cv2
import multiprocessing as mp
from queue import Empty
import os
import datetime


user_id     = "user-id"         # Change to match your camera setting
user_pw     = "password"        # Change to match your camera setting
host        = "192.168.0.10"    # Change to match your camera setting
winname     = "VIDEO"           # Window title
pathOut     = 'image'           # Image file save folder name
queue_max   = 30                # Maximum number of queues
save_max    = 100               # Number of files to save


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


def SaveImageProcess(imageQueue):
    '''
    [Abstract]
        Image file save task
    [Param]
        imageQueue :    [i] Queue to store images to save.
    [Return]
        None
    '''
    while True:
        try:
            image, filename = imageQueue.get(True, 10)  # timeout 10 sec.

            # Termination check: If type(image) is "int" and the value is -1, it ends.
            if type(image) == int:
                if image == -1:
                    break

            # ファイル保存
            cv2.imwrite(filename, image)

        except Empty: # timeout of q1.get()
            print("Timeout happen.")

    print("Finish SaveImageProcess()")


if __name__ == '__main__':
    '''
    [Abstract]
        main function
    '''
    cap = cv2.VideoCapture(f"rtsp://{user_id}:{user_pw}@{host}/MediaInput/stream_1")

    windowInitialized = False
    count = 0
    if not os.path.exists(pathOut):
        os.mkdir(pathOut)
        
    imageQueue = mp.Queue()
    starttime = datetime.datetime.now()

    p = mp.Process(target=SaveImageProcess, args=(imageQueue,))
    p.start()

    while True:
        try:
            ret, frame = cap.read()
            if ret == True:

                # File saving starts after 10 seconds or more have passed since the program started.
                if (datetime.datetime.now() - starttime).seconds > 10:
                    # Save file if queue size is within the upper limit.
                    if imageQueue.qsize() < queue_max:
                        # Save jpeg file.
                        count += 1
                        filename = os.path.join(pathOut, 'image_{:06d}.jpg'.format(count))
                        print(filename)
                        imageQueue.put([frame, filename])
                        if count >= save_max:
                            break

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

    # Terminate process p
    imageQueue.put([-1,-1])
    print("Wait for process p to finish")
    p.join()
    print("Finish main()")

    cap.release()
    cv2.destroyAllWindows()
