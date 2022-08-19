# importing libraries
from xmlrpc.client import boolean
import cv2
import numpy as np 
import math
import pyautogui as p
import time as t      

prev = 0
count = 5 

#Read Camera
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
def nothing(x):
    pass
 

while True:
    _,frame = cap.read()  
    frame = cv2.flip(frame,2)
    frame = cv2.resize(frame,(600,500))
    # Get hand data from the rectangle sub window
    cv2.rectangle(frame, (0,1), (300,500), (255, 0, 0), 0)
    crop_image = frame[1:500, 0:300]
    
    # Converting to HSV colors
    hsv = cv2.cvtColor(crop_image, cv2.COLOR_BGR2HSV)

    # detecting hand
    # setting color range
    lower_bound = np.array([90, 0, 0])
    upper_bound = np.array([136, 250, 250])
    # lower_bound = np.array([90, 60, 0])
    # upper_bound = np.array([120, 180, 250]) 

    
    # Creating Mask
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Filter mask with image
    filtr = cv2.bitwise_and(crop_image, crop_image, mask=mask)
    
    # Taking the forground
    mask1  = cv2.bitwise_not(mask)
    ret,thresh = cv2.threshold(mask1,0,255,cv2.THRESH_BINARY)
    dilata = cv2.dilate(thresh,(3,3),iterations = 6)
    
    #findcontour(img,contour_retrival_mode,method)
    cnts,hier = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    
    try:
        # Find contour with maximum area
        cm = max(cnts, key=lambda x: cv2.contourArea(x))
        epsilon = 0.0005*cv2.arcLength(cm,True)
        data= cv2.approxPolyDP(cm,epsilon,True)
    
        hull = cv2.convexHull(cm)
        
        cv2.drawContours(crop_image, [cm], -1, (255, 255, 0), 2)
        cv2.drawContours(crop_image, [hull], -1, (0, 255, 255), 2)
        
        # Find convexity defects
        hull = cv2.convexHull(cm, returnPoints=False)
        defects = cv2.convexityDefects(cm, hull)
        count_defects = 0

        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]
           
            start = tuple(cm[s][0])
            end = tuple(cm[e][0])
            far = tuple(cm[f][0])
            #Cosin Rule
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            angle = (math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180) / 3.14

            # if angle <= 50 draw a circle at the far point
            if angle <= 50:
                count_defects += 1
                cv2.circle(crop_image,far,5,[255,255,255],-1)
        
        print("\tFingers ==",count_defects+1)
        
        if count_defects == prev and count > 0:
            count -= 1
        if count_defects != prev:
            count = 5

        prev = count_defects

        if count_defects == 0:
            cv2.putText(frame, " ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2)
        elif count_defects == 1:
                if count == 0:
                    p.press("space")
                    count = 5
                cv2.putText(frame, "Play/Pause", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)
        elif count_defects == 2:
                if count == 0:
                    p.press("up")
                cv2.putText(frame, "Volume UP", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)
        elif count_defects == 3:
                if count == 0:
                    p.press("down")
                cv2.putText(frame, "Volume Down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)
        elif count_defects == 4:
                if count == 0:
                    p.press("right")
                cv2.putText(frame, "Forward", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)
        else:
            pass
        
        

    except:
        pass
    #step -10    
    cv2.imshow("Thresh", thresh)
    cv2.imshow("mask==",mask)
    cv2.imshow("filter==",filtr)
    cv2.imshow("Result", frame)

    key = cv2.waitKey(25) &0xFF    
    if key == 27: 
        break
cap.release()
cv2.destroyAllWindows()
    
    
  