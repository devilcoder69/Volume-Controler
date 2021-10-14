import cv2
import time
import numpy as np
import Hand_Tracking_Module as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


##############################

wCAm, hCam = 640, 480

##############################

cap = cv2.VideoCapture(0)
cap.set(3,wCAm)
cap.set(4,hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)

########## For Volume #########

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
# print(volRange)
# volume.SetMasterVolumeLevel(0, None)
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (255,0,0)

###############################



while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:

        # Filter based on size
        area = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1]) // 100
        # print('Area: ',area)

        if 70 < area < 500:
            # print("yes")
            length,img, lineInfo = detector.findDistance(4,8,img)
            # print('length: ',length)
            
            # Convert Volume
            volBar = np.interp(length,[20,150],[400, 150])
            volPer = np.interp(length,[20,150],[0, 100])

            smoothness = 10
            volPer = smoothness * round(volPer/smoothness)

            # check Fingers up
            fingers = detector.fingersUp()
            # print(fingers)


            # If pinky finger up
            if fingers[2]:
                volume.SetMasterVolumeLevelScalar(volPer/100,None)
                cv2.circle(img, (lineInfo[4],lineInfo[5]), 10,(0,255,0), cv2.FILLED)
                colorVol = (0,255,0)
                # time.sleep(0.10)
            else:
                colorVol = (255,0,0)



    # Drwaings
    cv2.rectangle(img, (50,150),(85,400),(255,0,0),3)
    cv2.rectangle(img, (50,int(volBar)),(85,400),(255,0,0),cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (40,140),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0), 2) #450
    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {int(cVol)}', (400,50),cv2.FONT_HERSHEY_COMPLEX,1,colorVol, 2)

    # Frame Rate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0), 2)

    cv2.imshow("Img", img)
    cv2.waitKey(1)

