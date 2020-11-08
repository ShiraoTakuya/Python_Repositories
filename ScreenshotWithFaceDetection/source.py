from PIL import ImageGrab
import cv2
import numpy as np

face_cascade_path = 'cv/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)

#Translate RGB to BGR
frame = cv2.cvtColor(np.asarray(ImageGrab.grab()), cv2.COLOR_BGR2RGB)
frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(frame_gray)

for x, y, w, h in faces:
	cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
	
cv2.imshow('image', frame)
cv2.waitKey(0)

cv2.destroyAllWindows()
