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
    Create a GUI application using tkinter.
    tkinter を使って GUI アプリケーションを作成します。
    
[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]
    cv2 :           pip install opencv-python
    PIL :           pip install pillow
'''

import cv2
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
import multiprocessing as mp
from queue import Empty
from classification_vgg import ImagenetClassificationVgg    # Local module. See 'classification_vgg.py'.


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

        # Create menu.
        menubar = tk.Menu(self.master)
        self.master.configure(menu=menubar)
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label='File', menu=filemenu)
        filemenu.add_command(label='Quit', command = self.on_closing_window)

        # Create button_frame
        self.button_frame = tk.Frame(self.master, padx=10, pady=10, relief=tk.RAISED, bd=2)
        self.button_frame.pack(side = tk.BOTTOM, fill=tk.X)

        # Label
        self.label_frame1 = tk.Frame(self.button_frame, width=10)
        self.label_frame1.pack(side=tk.LEFT)
        self.label_frame2 = tk.Frame(self.button_frame, width=40)
        self.label_frame2.pack(side=tk.LEFT)
        self.class_text = tk.StringVar()
        self.score_text = tk.StringVar()
        self.class_text.set('')
        self.score_text.set('')
        self.label1 = tk.Label(self.label_frame1, text='Class: ').pack(side=tk.TOP)
        self.label2 = tk.Label(self.label_frame2, textvariable=self.class_text, relief=tk.RIDGE, width=20).pack(side=tk.TOP)
        self.label3 = tk.Label(self.label_frame1, text='Score: ').pack(side=tk.TOP)
        self.label4 = tk.Label(self.label_frame2, textvariable=self.score_text, relief=tk.RIDGE, width=20).pack(side=tk.TOP)


        # Create quit_button
        self.quit_button = tk.Button(self.button_frame, text='Quit', width=10, command = self.on_closing_window)
        self.quit_button.pack(side=tk.RIGHT)
        
        # Create canvas.
        self.canvas = tk.Canvas(self.master)

        # Add mouse click event to canvas.
        self.canvas.bind('<Button-1>', self.canvas_click)

        # Place canvas.
        self.canvas.pack(expand = True, fill = tk.BOTH)

        # Create queue and value for image receive process.
        self.imageQueue = mp.Queue()
        self.request = mp.Value('i', 0)     # -1 : Exit ReceiveImageProcess.
                                            #  0 : Normal.
                                            #  1 : Connect camera.
                                            #  2 : Release camera.

        # Create queue for classification process.
        self.imageQueue2 = mp.Queue()
        self.resultQueue = mp.Queue()

        # Create processes.
        self.imageReceiveProcess = mp.Process(target=ReceiveImageProcess, args=(self.imageQueue, self.imageQueue2, self.request))
        self.classificationProcess = mp.Process(target=ImageClassificationProcess, args=(self.imageQueue2, self.resultQueue))
        self.imageReceiveProcess.start()
        self.classificationProcess.start()

        # Raise a video display event (disp_image) after 500m
        self.disp_id = self.after(500, self.disp_image)

    def on_closing_window(self):
        ''' Window closing event. '''

        if messagebox.askokcancel("QUIT", "Do you want to quit?"):
            # Request terminate process.
            self.request.value = -1
            self.imageQueue2.put(-1)

            # Waiting for process p to finish
            time.sleep(1)

            # Flash queue.
            # The program cannot complete processes unless the queue is emptied.
            for i in range(self.imageQueue.qsize()):
                image = self.imageQueue.get()
            for i in range(self.imageQueue2.qsize()):
                image = self.imageQueue2.get()
            for i in range(self.resultQueue.qsize()):
                result = self.resultQueue.get()

            # Wait for process to be terminated.
            self.imageReceiveProcess.join()
            self.classificationProcess.join()
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

        # Update GUI Label.
        result_num = self.resultQueue.qsize()
        if result_num > 0:
            for i in range(result_num):
                label, score = self.resultQueue.get()
            self.class_text.set(label)
            score = '{:.4f}'.format(score)
            self.score_text.set(score)
            
        # Raise a video display event (disp_image) after 1ms.
        self.disp_id = self.after(1, self.disp_image)


def ReceiveImageProcess(imageQueue, imageQueue2, request):
    '''
    Receive Image Process.

    Args:
        imageQueue      [o] Image data for display.
        imageQueue2     [o] Image data for image classification.
        request         [i] Shared memory for receiving requests from the main process.
                            -1: Terminate process.
                             0: Nothing.
                             1: Connect camera.
                             2: Release camera connection.
    Returns:
        None
    Raises
        None
    '''

    # Connect camera.
    cap = cv2.VideoCapture(url)

    while True:
        if cap != None:
            # Get frame.
            ret, frame = cap.read()

            if ret == True:
                # (1) Convert image from BGR to RGB.
                cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # for display.
                if imageQueue.qsize() < 10:
                    imageQueue.put(cv_image)
                
                # for image classification.
                if imageQueue2.qsize() <= 1:
                    imageQueue2.put(cv_image)

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

    print("Terminate ReceiveImageProcess().")


def ImageClassificationProcess(imageQueue, resultQueue):
    '''
    Image classification process.

    Args:
        imageQueue :        [i] Image for image classification.
        resultQueue :       [o] Save classification result labels and scores.
    Returns:
        None
    '''
    imagenetClassifigationVgg = ImagenetClassificationVgg('./data/imagenet_class_index.json')

    while True:
        try:
            image = imageQueue.get(True, 10)

            # If type(image) is 'int' and image is -1, then this process is terminated.
            if type(image) == int:
                if image == -1:
                    break

            # Image classification
            pilImage = Image.fromarray(image)   # convert from OpenCV image to PIL.Image
            result, score = imagenetClassifigationVgg.do_classification(pilImage)

            if score > 0.15:
                print(result, score)
                resultQueue.put((result, score))
            else:
                print('None')
                resultQueue.put(('None', 0.0))

        except Empty: # timeout of imageQueue.get()
            print("Timeout happen.(3)")

    print("Finish ImageClassificationProcess()")    


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master = root)
    app.mainloop()
