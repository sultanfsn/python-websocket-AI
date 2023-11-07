import cv2
import base64
import numpy as np

def from_b64(uri):
    '''
        Convert from b64 uri to OpenCV image
        Sample input: 'data:image/jpg;base64,/9j/4AAQSkZJR......'
    '''
    encoded_data = uri.split(',')[1]
    data = base64.b64decode(encoded_data)
    np_arr = np.fromstring(data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def to_b64(img):
    '''
        Convert from OpenCV image to b64 uri
        Sample output: 'data:image/jpg;base64,/9j/4AAQSkZJR......'
    '''
    _, buffer = cv2.imencode('.jpg', img)
    uri = base64.b64encode(buffer).decode('utf-8')
    return f'data:image/jpg;base64,{uri}'

def grayscale(data):
    try:
        img = from_b64(data)
        # Do some OpenCV Processing
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # End for OpenCV Processing
        
        return to_b64(img)
    except:
        # just in case some process is failed
        # normally, for first connection
        # return the original data
        return data
    
def haarcascade(data):
    try:
        img = from_b64(data)
        detector=cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier('Haarcascades/haarcascade_eye.xml')
        faces=detector.detectMultiScale(img,1.1,7)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #Draw the rectangle around each face
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

        return to_b64(img)
    
    except:
        print("a")
        return data
