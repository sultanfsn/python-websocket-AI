import json
from flask import Flask,render_template,Response, request
import cv2
from flask_sock import Sock
from service.visual_manipulation import grayscale, haarcascade
import pusher

app=Flask(__name__)
sock = Sock(app)
camera=cv2.VideoCapture(0)

pusher_client = pusher.Pusher(app_id=u'APP_ID', key=u'APP_KEY', secret=u'SECRET', cluster=u'mt1')

def generate_frames():
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            img = cv2.imread('test.jpg')
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            detector=cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
            eye_cascade = cv2.CascadeClassifier('Haarcascades/haarcascade_eye.xml')
            faces=detector.detectMultiScale(frame,1.1,7)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
             #Draw the rectangle around each face
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@sock.route("/ws")
def websocket_endpoint(ws):
    while True:
        # print("a")
        data = ws.receive()
        ws.send(haarcascade(data))

@app.route("/pusher/auth", methods=['POST'])
def pusher_authentication():

  # This authenticates every user. Don't do this in production!
  # pusher_client is obtained through pusher.Pusher( ... )
  auth = pusher_client.authenticate(
    channel=request.form['channel_name'],
    socket_id=request.form['socket_id']
  )
  return json.dumps(auth)


    # await websocket.accept()
    # while True:
    #     data = await websocket.receive_text()
    #     await websocket.send_text( grayscale(data) )

if __name__=="__main__":
    app.run(debug=True)

