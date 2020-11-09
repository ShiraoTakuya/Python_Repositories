import dlib
from imutils import face_utils
from PIL import ImageGrab
import cv2
import numpy as np

face_detector = dlib.get_frontal_face_detector()

predictor_path = 'shape_predictor_68_face_landmarks.dat'
face_predictor = dlib.shape_predictor(predictor_path)

camera = cv2.VideoCapture(0)

while True:
	ret, img = camera.read()
	img_gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	faces = face_detector(img_gry, 1)

	for face in faces:
	    landmark = face_predictor(img_gry, face)
	    landmark = face_utils.shape_to_np(landmark)

	    for (i, (x, y)) in enumerate(landmark):
	        cv2.circle(img, (x, y), 1, (255, 0, 0), -1)
	cv2.imshow('sample', img)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

camera.release()
cv2.destroyAllWindows()
