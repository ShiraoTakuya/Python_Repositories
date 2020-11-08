import cv2

face_cascade_path = 'cv/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)
camera = cv2.VideoCapture(0)

while True:
	ret, frame = camera.read()
	frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(frame_gray)

	for x, y, w, h in faces:
		cv2.imshow('camera', frame[y: y + h, x: x + w])

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

camera.release()
cv2.destroyAllWindows()
