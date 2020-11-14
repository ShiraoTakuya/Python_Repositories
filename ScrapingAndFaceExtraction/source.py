import requests
import urllib.request
import time
import re
import cv2
import io
import numpy as np
from PIL import Image

URL = "https://search.yahoo.co.jp/image/search?p=%E7%BE%8E%E4%BA%BA&ei=UTF-8&b=&aq=-1&oq="

face_cascade_path = 'cv/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)

def bin_to_bgr(img_bin):
    img_pil = Image.open(io.BytesIO(img_bin))
    return cv2.cvtColor(np.asarray(img_pil), cv2.COLOR_RGBA2BGR)

def get_img_src_list(url):
    response = requests.get(url)
    img_src_list = [m for m in re.findall("\"detailUrl\":\"(https?://[\w/:%#\$&\?\(\)~\.=\+\-]+)\"", response.text)]
    return img_src_list

def download_img(src, dist_path):
    time.sleep(1)
    with urllib.request.urlopen(src) as data:
        img_bin = data.read()
        img = bin_to_bgr(img_bin)
        frame_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(frame_gray)
        for i, (x,y,w,h) in enumerate(faces):
            cv2.imwrite(dist_path+f'_{i}.jpg', img[y: y + h, x: x + w])

def main():
    img_src_list = get_img_src_list(URL)
    for i, src in enumerate(img_src_list):
        print(f'downloading...: {src}')
        try:
            download_img(src, f'./img/face_{i}')
        except:
            pass

main()
