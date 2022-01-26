#Program ini khas untuk kumpulan 1 dari pengajian Machine Vision yang diterajui oleh:
#Ainul Hakim
#Hazmi Naquiddin
#Hisaym Saad
#Segala kaedah dan cara adalah agi tujuan pembelajaran
import requests
import cv2
import mediapipe as mp
import numpy as np
import imutils
import time
#Declaration
typeC = 0
timerDetectStart = time.time()
timerDetectEnd = timerDetectStart

#Face Detection
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

#Face Drawing
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

#Open Webcam
#cap = cv2.VideoCapture(0)
url = "http://10.209.104.32:8080/shot.jpg"

#Start Loop
#while cap.isOpened():
while True:
    img_resp = requests.get(url)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)
    img = imutils.resize(img, width=1000, height=1800)
    cv2.imshow("Android_cam", img)

    #Check Webcam
    #success, img = cap.read()
    
    #Declaration in Loop
    start = time.time()
    timerDetectLap = start - timerDetectEnd
    timerDetectTotal = start - timerDetectStart

    #Store img in RGB and BGR
    img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
    img.flags.writeable = False
    results = face_mesh.process(img)
    img.flags.writeable = True
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    #Declare img
    img_h, img_w, img_c = img.shape
    face_3d = []
    face_2d = []

    #Condition img Detect
    if results.multi_face_landmarks:
        #Loop img Detect
        for face_landmarks in results.multi_face_landmarks:
            for idx, lm in enumerate(face_landmarks.landmark):
                #Condition Landmark
                if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                    if idx == 1:
                        nose_2d = (lm.x * img_w, lm.y * img_h)
                        nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)

                    x, y = int(lm.x * img_w), int(lm.y * img_h)

                    # Get the 2D Coordinates
                    face_2d.append([x, y])

                    # Get the 3D Coordinates
                    face_3d.append([x, y, lm.z])       
            
            # Convert it to the NumPy array
            face_2d = np.array(face_2d, dtype=np.float64)

            # Convert it to the NumPy array
            face_3d = np.array(face_3d, dtype=np.float64)

            # The camera matrix
            focal_length = 1 * img_w

            cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                    [0, focal_length, img_w / 2],
                                    [0, 0, 1]])

            # The distortion parameters
            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            # Solve PnP
            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

            # Get rotational matrix
            rmat, jac = cv2.Rodrigues(rot_vec)

            # Get angles
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

            # Get the y rotation degree
            x = angles[0] * 360
            y = angles[1] * 360
            z = angles[2] * 360
          

            #Condition user's head tilting
            if y < -10:
                text = "Suspicious"
                typeC=1
                
            elif y > 10:
                text = "Suspicious"
                typeC=1
                
            elif x < -10:
                text = "Suspicious"
                typeC=1
                
            elif x > 10:
                text = "Suspicious"
                typeC=1
                
            else:
                text = "Focus"
                typeC=2
                timerDetectEnd = time.time()

            #Condition Cheatng
            if typeC == 1:
                if timerDetectLap > 5:
                    text = "Cheating"
                    cv2.putText(img, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                else:
                    cv2.putText(img, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 128, 255), 2)
            else:
                cv2.putText(img, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 34), 2)

            # Display the nose direction
            nose_3d_projection, jacobian = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)
            p1 = (int(nose_2d[0]), int(nose_2d[1]))
            p2 = (int(nose_2d[0] + y * 10) , int(nose_2d[1] - x * 10))
            cv2.line(img, p1, p2, (255, 0, 0), 3)

            # Add the text on the img
            #cv2.putText(img, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 128, 255), 2) BGR
            cv2.putText(img, "x: " + str(np.round(x,2)), (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(img, "y: " + str(np.round(y,2)), (500, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(img, "z: " + str(np.round(z,2)), (500, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


        end = time.time()
        totalTime = end - start
        

        fps = 1 / totalTime
        #print("FPS: ", fps)

        #cv2.putText(img, f'FPS: {int(fps)}', (20,450), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
        cv2.putText(img, f'Time Lap: {int(timerDetectLap)}', (300,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(img, f'Total Time: {int(timerDetectTotal)}', (20,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        mp_drawing.draw_landmarks(
                    img=img,
                    landmark_list=0,#face_landmarks,
                    #connections=mp_face_mesh.FACE_CONNECTIONS,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec)


    cv2.imshow('Head Pose Estimation', img)

    if cv2.waitKey(5) & 0xFF == 27:
        break

   
#cap.release()
    # Press Esc key to exit
    if cv2.waitKey(1) == 27:
        break
  
cv2.destroyAllWindows()