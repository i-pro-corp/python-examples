# python-examples

We publish sample programs here that connect to an i-PRO camera and display images on a PC. These are intended for beginners.  
i-PRO カメラと接続して映像表示するＰＣプログラムのサンプルです。初心者を対象としています。

---

## Connect to an i-PRO camera with RTSP(H.264/H.265)

関連記事：[RTSP で接続する](https://i-pro-corp.github.io/Programing-Items/Python/connect_camera/connect_with_rtsp.html)

| Filename                  | Abstract                                                      |
|:--------------------------|:--------------------------------------------------------------|
| connect_with_rtsp_1.py    | Let's try first.                                              |
| connect_with_rtsp_2.py    | Let's improve the three issues.                               |
| connect_with_rtsp_3_1.py  | Let's add face detection using OpenCV.                        |
| connect_with_rtsp_3_2.py  | Improve performace by a face detection process.               |
| connect_with_rtsp_4.py    | Save the received image as a JPEG file.                       |
| connect_with_rtsp_5.py    | Add reconnection when video is disconnected.                  |
| connect_with_rtsp_6_1.py  | Display the video with GUI using tkinter.                     |
| connect_with_rtsp_6_2.py  | Improve performance by a video receiving process.             |
| connect_with_rtsp_6_3.py  | Add a menu and a button to make it look like a GUI app.       |

---

## Connect to an i-PRO camera with JPEG

関連記事：[JPEG で接続する](https://i-pro-corp.github.io/Programing-Items/Python/connect_camera/connect_with_jpeg.html)

| Filename                  | Abstract                                                      |
|:--------------------------|:--------------------------------------------------------------|
| connect_with_jpeg_1.py    | Let's try first.                                              |
| connect_with_jpeg_2.py    | Let's improve the three issues.                               |
| connect_with_jpeg_3.py    | Let's add face detection using OpenCV.                        |
| connect_with_jpeg_4.py    | Save the received image as a JPEG file.                       |
| connect_with_jpeg_5.py    | Add reconnection when video is disconnected.                  |
| connect_with_jpeg_6.py    | Display the video with GUI using tkinter.                     |

---

## Connect to an i-PRO camera with MJPEG

関連記事：[MJPEG で接続する](https://i-pro-corp.github.io/Programing-Items/Python/connect_camera/connect_with_mjpeg.html)

| Filename                  | Abstract                                                      |
|:--------------------------|:--------------------------------------------------------------|
| connect_with_mjpeg_1_1.py | Let's try first. (Method 1)                                   |
| connect_with_mjpeg_1_2.py | Let's try first. (Method 2)                                   |
| connect_with_mjpeg_2.py   | Let's improve the three issues.                               |
| connect_with_mjpeg_3_1.py | Let's add face detection using OpenCV.                        |
| connect_with_mjpeg_3_2.py | Improve performace by a face detection process.               |
| connect_with_mjpeg_4.py   | Save the received image as a JPEG file.                       |
| connect_with_mjpeg_5.py   | Add reconnection when video is disconnected.                  |
| connect_with_mjpeg_6.py   | Display the video with GUI using tkinter.                     |

---

## Connect to wv-xae200w

関連記事：[機能拡張ソフトウェア(WV-XAE200WUX)と接続する](https://i-pro-corp.github.io/Programing-Items/Python/connect_camera/connect_to_wv-xae200w.html)

| Filename                  | Abstract                                                                    |
|:--------------------------|:----------------------------------------------------------------------------|
| parse_jpeg.py             | Extracts the recognition result of WV-XAE200WUX from the JPEG file.         |
| draw_aivmd_rect.py        | Draws the recognition result of WV-XAE200WUX on the received image.         |
| show_live_camera.py       | Draws the recognition result of WV-XAE200WUX on the live video.             |

---

## Image classification

関連記事：[画像分類 - VGG16](https://i-pro-corp.github.io/Programing-Items/Python/connect_camera/image_classification_vgg.html)

| Filename                        | Abstract                                                              |
|:--------------------------------|:----------------------------------------------------------------------|
| preparation.py                  | Preparation for image classification.                                 |
| classification_vgg.py           | Image classification.                                                 |
| classification_main.py          | How to write a program simply using classification_vgg.py             |
| classification_with_camera_1.py | Classifies live images.                                               |
| classification_with_camera_2.py | Classifies live images with multitasking.                             |
| classification_gui.py           | Create a GUI application using tkinter.                               |

---

## MobileNet-SSD

関連記事：[物体検知 － MobileNet-SSD](https://i-pro-corp.github.io/Programing-Items/Python/connect_camera/mobilenet-ssd.html)

| Filename                                       | Abstract                                                                        |
|:-----------------------------------------------|:--------------------------------------------------------------------------------|
| run_mobilenetv3-ssdlite_jpeg_demo.py           | Detect objects in JPEG images using the "MobileNetV3 SSD-Lite"                  |
| run_mobilenetv3-ssdlite_live_pc-cam_demo.py    | Detect objects in the pc camera live video using the "MobileNetV3 SSD-Lite".    |
| run_mobilenetv3-ssdlite_live_i-pro-cam_demo.py | Detect objects in the i-pro camera live video using the "MobileNetV3 SSD-Lite". |
