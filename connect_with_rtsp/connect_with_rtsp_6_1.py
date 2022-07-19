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
    tkinter を使ったGUIで映像を表示します。
    BGR → RGB
    numpy.ndarray → PIL.Image → ImageTk.PhotoImage
    (1) BGR → RGB
    (2) numpy.ndarray → PIL.Image
    (3) PIL.Image → ImageTk.PhotoImage

[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    cv2:    pip install opencv-python
    PIL :   pip install pillow
'''

#from urllib.parse import non_hierarchical
import cv2
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps


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

        # Raise a video display event (disp_image) after 500m
        self.cap = None
        self.disp_id = self.after(500, self.disp_image)

    def on_closing_window(self):
        ''' Window closing event. '''
        
        if messagebox.askokcancel("QUIT", "Do you want to quit?"):
            self.master.destroy()
            print("Finish Application.")

    def canvas_click(self, event):
        ''' Event handling with mouse clicks on canvas '''

        if self.disp_id is None:
            # Connect camera.
            self.cap = cv2.VideoCapture(url)
            # Display image.
            self.disp_image()

        else:
            # Release camera.
            self.after_cancel(self.disp_id)
            self.disp_id = None
            self.cap.release()

    def disp_image(self):
        ''' Display image on Canvas '''

        if self.cap == None:
            # Connect camera.
            self.cap = cv2.VideoCapture(url)

        # Get frame.
        ret, frame = self.cap.read()

        if ret == True:
            # (1) Convert image from BGR to RGB.
            cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # (2) Convert image from ndarray to PIL.Image.
            pil_image = Image.fromarray(cv_image)

            # Get canvas size.
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Resize the image to the size of the canvas without changing the aspect ratio.
            # アスペクトを維持したまま画像を Canvas と同じサイズにリサイズ
            pil_image = ImageOps.pad(pil_image, (canvas_width, canvas_height))

            # (3) Convert image from PIL.Image to PhotoImage
            self.photo_image = ImageTk.PhotoImage(image=pil_image)

            # Display image on the canvas.
            self.canvas.create_image(
                canvas_width / 2,       # Image display position (center of the canvas)
                canvas_height / 2,                   
                image=self.photo_image  # image data
                )
            
        else:
            print("cap.read() return False.")
            # The timeout period seems to be 30 seconds.
            # And there seems to be no API to change the timeout value.
            time.sleep(1)

            # Reconnect
            self.cap.release()
            self.cap = cv2.VideoCapture(url)

        # Raise a video display event (disp_image) after 1ms.
        self.disp_id = self.after(1, self.disp_image)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master = root)
    app.mainloop()
