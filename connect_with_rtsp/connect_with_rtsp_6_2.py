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
    RTSP で i-PRO カメラと接続してみる。

[Details]
    Display the video with GUI using tkinter.
    Try to improve performance by creating a video receiving process.
    
    tkinter を使ったGUIで映像を表示します。
    映像受信プロセスを作成することでパフォーマンス改善を試みます。

    BGR → RGB
    numpy.ndarray → PIL.Image → ImageTk.PhotoImage
    (1) BGR → RGB
    (2) numpy.ndarray → PIL.Image
    (3) PIL.Image → ImageTk.PhotoImage
    
[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    pip install opencv-python
    pip install pillow
'''

import cv2
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
import multiprocessing as mp


user_id     = "user-id"         # Change to match your camera setting
user_pw     = "password"        # Change to match your camera setting
host        = "192.168.0.10"    # Change to match your camera setting
winname     = "VIDEO"           # Window title
url         = f"rtsp://{user_id}:{user_pw}@{host}/MediaInput/stream_1"


class Application(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.pack()

        # Window settings.
        self.master.title("Display i-PRO camera with tkinter")      # Window title
        self.master.geometry("800x600+100+100")                     # Window size, position

        # Event registration for window termination.
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing_window)
        
        # Create canvas.
        self.canvas = tk.Canvas(self.master)

        # Add mouse click event to canvas.
        self.canvas.bind('<Button-1>', self.canvas_click)

        # Place canvas.
        self.canvas.pack(expand = True, fill = tk.BOTH)

        # Create image receiving process and queue
        self.imageQueue = mp.Queue()
        self.request = mp.Value('i', 0)     # -1 : Exit ReceiveImageProcess.
                                            #  0 : Normal.
                                            #  1 : Connect camera.
                                            #  2 : Release camera.
        self.p = mp.Process(target=ReceiveImageProcess, args=(self.imageQueue, self.request))
        self.p.start()

        # Raise a video display event (disp_image) after 500m
        self.disp_id = self.after(500, self.disp_image)

    def on_closing_window(self):
        ''' Window closing event. '''

        if messagebox.askokcancel("QUIT", "Do you want to quit?"):
            # Request terminate process self.p.
            self.request.value = -1

            # Waiting for process p to finish
            time.sleep(1)

            # Flash buffer.
            # The program cannot complete p.join() unless the imageQueue is emptied.
            for i in range(self.imageQueue.qsize()):
                pil_image = self.imageQueue.get()

            # Wait for process p to be terminated.
            self.p.join()
            self.master.destroy()
            print("Finish Application.")

    def canvas_click(self, event):
        ''' Event handling with mouse clicks on canvas '''

        if self.disp_id is None:
            # Connect camera.
            self.request.value = 1
            # Display image.
            self.disp_image()

        else:
            # Release camera.
            self.request.value = 2
            # Cancel scheduling
            self.after_cancel(self.disp_id)
            self.disp_id = None

    def disp_image(self):
        ''' Display image on Canvas '''

        # If there is data in the imageQueue, the program receives the data and displays the video.
        num = self.imageQueue.qsize()
        if num > 0:
            if (num > 5):
                num -= 1
            for i in range(num):
                cv_image = self.imageQueue.get()

            # (2) Convert image from ndarray to PIL.Image.
            pil_image = Image.fromarray(cv_image)

            # Get canvas size.
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Resize the image to the size of the canvas without changing the aspect ratio.
            # アスペクトを維持したまま画像を Canvas と同じサイズにリサイズ
            pil_image = ImageOps.pad(pil_image, (canvas_width, canvas_height))

            # (3) Convert image from PIL.Image to PhotoImage
            # PIL.Image から PhotoImage へ変換する
            self.photo_image = ImageTk.PhotoImage(image=pil_image)

            # Display image on the canvas.
            self.canvas.create_image(
                canvas_width / 2,       # Image display position (center of the canvas)
                canvas_height / 2,                   
                image=self.photo_image  # image data
                )
            
        else:
            pass

        # Raise a video display event (disp_image) after 1ms.
        self.disp_id = self.after(1, self.disp_image)


def ReceiveImageProcess(imageQueue, request):
    """
    Receive Image Process.

    Args:
        imageQueue      [o] This process stores the received image data in the imageQueue.
        request         [i] Shared memory for receiving requests from the main process.
                            -1: Terminate process.
                             0: Nothing.
                             1: Connect camera.
                             2: Release camera connection.
    Returns:
        None
    Raises
        None
    """

    # Connect camera.
    cap = cv2.VideoCapture(url)

    while True:
        if cap != None:
            # Get frame.
            ret, frame = cap.read()

            if ret == True:
                # (1) Convert image from BGR to RGB.
                cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                if imageQueue.qsize() < 10:
                    imageQueue.put(cv_image)

            else:
                print("cap.read() return False.")
                # The timeout period seems to be 30 seconds.
                # And there seems to be no API to change the timeout value.
                time.sleep(1)

                # Reconnect
                cap.release()
                cap = cv2.VideoCapture(url)
        else:
            time.sleep(0.1)
                
        # Check process termination request.
        if request.value == -1:
            # Terminate process.
            cap.release()
            request.value = 0
            break

        # Check connect request.
        if request.value == 1:
            cap = cv2.VideoCapture(url)
            request.value = 0

        # Check release request.
        if request.value == 2:
            cap.release()
            cap = None
            request.value = 0

    print("Terminate SaveImageProcess().")


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master = root)
    app.mainloop()
