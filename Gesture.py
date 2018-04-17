import cv2
import numpy as np
import math
import time
import pyautogui


pyautogui.FAILSAFE = False
SCREEN_X, SCREEN_Y = pyautogui.size()
CLICK = CLICK_MESSAGE = MOVEMENT_START = None

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    CAMERA_X, CAMERA_Y, channels = frame.shape
    frame = cv2.flip(frame, 1)
    cv2.rectangle(frame, (700, 300), (300, 0), (0, 255, 0), 0)
    crop_img = frame[0:300, 300:700]
    grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    value = (35, 35)
    blurred = cv2.GaussianBlur(grey, value, 0)
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # check OpenCV version to avoid unpacking error
    (version, _, _) = cv2.__version__.split('.')

    if version == '3':
        image, contours, hierarchy = cv2.findContours(thresh1.copy(), \
                                                     cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    elif version == '2':
        contours, hierarchy = cv2.findContours(thresh1.copy(), cv2.RETR_TREE, \
                                              cv2.CHAIN_APPROX_NONE)

    cnt = max(contours, key=lambda x: cv2.contourArea(x))

    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(crop_img, (x, y), (x + w, y + h), (0, 0, 255), 0)
    
    # finding convex hull
    hull = cv2.convexHull(cnt)

    # drawing contours
    drawing = np.zeros(crop_img.shape, np.uint8)
    cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
    cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 0)
    
    # finding convex hull
    hull = cv2.convexHull(cnt, returnPoints=False)

    # finding convexity defects
    defects = cv2.convexityDefects(cnt, hull)
    count_defects = 0
    cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)

    used_defect = None
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57
        if angle <= 90:
            count_defects += 1
        cv2.circle(crop_img, far, 5, [0, 0, 255], -1)
        cv2.line(crop_img, start, end, [0, 255, 0], 2)
        medium_x = (start[0] + end[0]) / 2
        medium_y = (start[1] + end[1]) / 2

        if count_defects == 2 and angle <= 90:
            used_defect = {"x": start[0], "y": start[1]}

    if used_defect is not None:
        best = used_defect
        if count_defects == 2:
            x = best['x']
            y = best['y']
            display_x = x
            display_y = y

            if MOVEMENT_START is not None:
                M_START = (x, y)
                x = x - MOVEMENT_START[0]
                y = y - MOVEMENT_START[1]
                x = x * (SCREEN_X / CAMERA_X)
                y = y * (SCREEN_Y / CAMERA_Y)
                MOVEMENT_START = M_START
                print("X: " + str(x) + " Y: " + str(y))
                pyautogui.moveRel(x, y)
            else:
                MOVEMENT_START = (x, y)

            cv2.circle(crop_img, (display_x, display_y), 5, [255, 255, 255], 20)
        elif count_defects == 3 and CLICK is None:
            CLICK = time.time()
            pyautogui.click()
            CLICK_MESSAGE = "LEFT CLICK"

        elif count_defects == 1 and CLICK is None:
            CLICK = time.time()
            pyautogui.doubleClick()
            CLICK_MESSAGE = "DOUBLE CLICK"

        elif count_defects == 4 and CLICK is None:
            CLICK = time.time()
            pyautogui.rightClick()
            CLICK_MESSAGE = "RIGHT CLICK"
    else:
        MOVEMENT_START = None

    if CLICK is not None:
        cv2.putText(frame, CLICK_MESSAGE, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 3, 3)
        if CLICK < time.time():
             CLICK = None

    cv2.putText(frame, "Defects: " + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
    cv2.imshow('Gesture', frame)
    cv2.imshow('Drawing', drawing)

    k = cv2.waitKey(10)
    if k == 27:
        break
