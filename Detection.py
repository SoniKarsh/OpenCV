import cv2
import numpy as np
from pynput.mouse import Button, Controller
import wx

app = wx.App(False)
mouse = Controller()
(camx,camy) = (320,240)
(camxl,camyl) = (200,150)

def start_action(e):

    global mouse
    (sx,sy) = wx.GetDisplaySize()


    # [33,80,40]
    # [102,255,255]
    # [40,74,160]
    # [90,147,255]
    lowerBond = np.array([40,74,90])
    upperBond = np.array([77,255,255])

    cam = cv2.VideoCapture(0)
    cam.set(3,camx)
    cam.set(4,camy)
    kernelOpen = np.ones((5,5))
    kernelClose = np.ones((8,8))

    mLocOld=np.array([0,0])
    mouseLoc=np.array([0,0])
    DampingFactor = 3

    pinchFlagRight = 0
    pinchFlagLeft = 0
    pinchFlag = 0
    while (True):
        if e.is_set():
            cam.release()
            cv2.destroyAllWindows()
            e.clear()
        ret,img = cam.read()
        img = cv2.flip(img,1)
        if ret == True:
            pass
        else:
            break
        imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(imgHSV,lowerBond,upperBond)

        maskOpen = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
        maskClose = cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)

        a,b,c,d = 310,10,230,10
        cv2.rectangle(img,(a,c),(a+b,c+d),(255,0,0),2)
        maskFinal = maskClose
        _,conts,h = cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)


        # mouse movement
        if(len(conts)==3):
            if(pinchFlagRight == 1):
                pinchFlagRight=0
                mouse.release(Button.right)
                # print "right release"
            if(pinchFlagLeft == 1):
                pinchFlagLeft = 0
                mouse.release(Button.left)
                # print "left release"

            x1,y1,w1,h1 = cv2.boundingRect(conts[0])
            x2,y2,w2,h2 = cv2.boundingRect(conts[1])
            x3,y3,w3,h3 = cv2.boundingRect(conts[2])
            cv2.rectangle(img,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
            cv2.rectangle(img,(x2,y2),(x2+w2,y2+h2),(255,0,0),2)
            cv2.rectangle(img,(x3,y3),(x3+w3,y3+h3),(255,0,0),2)
            cx1 = x1+w1/2
            cy1 = y1+h1
            cx2 = x2+w2/2
            cy2 = y2+h2
            cx3 = x3+w3/2
            cy3 = y3+h3

            cx1,cy1 = dimension_converter(cx1,cy1)
            cx2,cy2 = dimension_converter(cx2,cy2)
            cx3,cy3 = dimension_converter(cx3,cy3)
            cx,cy = cx1,cy1
            if(cy<cy2):
                cx = cx2
                cy = cy2
            if(cy<cy3):
                cx = cx3
                cy = cy3


            cv2.line(img,(cx1,cy1),(cx2,cy2),(255,0,),2)
            cv2.line(img,(cx1,cy1),(cx3,cy3),(255,0,),2)
            cv2.circle(img,(cx,cy),2,(0,0,255),2)
            mouseLoc = mLocOld+((cx,cy)-mLocOld)/DampingFactor

            mousePosition = [mouseLoc[0]*sx/camxl,mouseLoc[1]*sy/camyl]
            if(mousePosition[0]>=sx):
                mousePosition[0]=sx-1
            if(mousePosition[1]>=sy):
                mousePosition[1]=sy-1
            mouse.position=(mousePosition[0],mousePosition[1])
            while mouse.position!=(mousePosition[0],mousePosition[1]):
                pass
            mLocOld = mouseLoc


        # Left and Right click
        elif(len(conts)==2):

            x1,y1,w1,h1 = cv2.boundingRect(conts[0])
            x2,y2,w2,h2 = cv2.boundingRect(conts[1])
            if(cv2.contourArea(conts[0])>cv2.contourArea(conts[1])):

                # if(w1*h1<w2+h2):
                #     t1,t1,t3,t4 = x1,y1,w1,h1
                #     x1,y1,w1,h1 = x2,y2,w2,h2
                #     x2,y2,w2,h2 = t1,t1,t3,t4

                cv2.rectangle(img,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
                cv2.rectangle(img,(x2,y2),(x2+w2,y2+h2),(255,0,0),2)
                cx1 = x1+w1/2
                cy1 = y1+h1
                cx2 = x2+w2/2
                cy2 = y2+h2

                cx1,cy1 = dimension_converter(cx1,cy1)
                cx2,cy2 = dimension_converter(cx2,cy2)
                if(cy1>cy2):
                    cx = cx1
                    cy = cy1
                else:
                    cx = cx2
                    cy = cy2

                cv2.circle(img,(cx,cy),2,(0,0,255),2)
                if(x1>x2):
                    if(pinchFlagRight == 0):
                        mouse.press(Button.right)
                        pinchFlagRight=1
                        # print "right press"
                else:
                    if(pinchFlagLeft == 0):
                        mouse.press(Button.left)
                        pinchFlagLeft =1
                        # print "left press"
                mouseLoc = mLocOld+((cx,cy)-mLocOld)/DampingFactor

                mousePosition = [mouseLoc[0]*sx/camxl,mouseLoc[1]*sy/camyl]
                if(mousePosition[0]>=sx):
                    mousePosition[0]=sx-1
                if(mousePosition[1]>=sy):
                    mousePosition[1]=sy-1
                mouse.position=(mousePosition[0],mousePosition[1])
                while mouse.position!=(mousePosition[0],mousePosition[1]):
                    pass
                mLocOld = mouseLoc
            else:
                pass

        # Scroll
        elif(len(conts)==1):
            if(pinchFlagRight == 1):
                pinchFlagRight=0
                mouse.release(Button.right)
                # print "right release"
            if(pinchFlagLeft == 1):
                pinchFlagLeft = 0
                mouse.release(Button.left)
                # print "left release"
            x1,y1,w1,h1 = cv2.boundingRect(conts[0])
            cx1 = x1+w1/2
            cy1 = y1+h1
            cx,cy = dimension_converter(cx1,cy1)
            scrollAmount = ((cx,cy)-mLocOld)/DampingFactor
            mouse.scroll(scrollAmount[0]*sx/camxl,scrollAmount[1]*sy/camyl)
            print "scroll"
            mouseLoc = mLocOld+((cx,cy)-mLocOld)/DampingFactor

            mousePosition = [mouseLoc[0]*sx/camxl,mouseLoc[1]*sy/camyl]
            if(mousePosition[0]>=sx):
                mousePosition[0]=sx-1
            if(mousePosition[1]>=sy):
                mousePosition[1]=sy-1
            mouse.position=(mousePosition[0],mousePosition[1])
            while mouse.position!=(mousePosition[0],mousePosition[1]):
                pass
            mLocOld = mouseLoc

        else:
            if(pinchFlagRight == 1):
                pinchFlagRight=0
                mouse.release(Button.right)
            if(pinchFlagLeft == 1):
                pinchFlagLeft = 0
                # print "right release"
                mouse.release(Button.left)
                # print "left release"

        cv2.imshow("maskClose",maskClose)
        cv2.imshow("maskOpen",maskOpen)
        cv2.imshow("mask",mask)
        cv2.imshow("img",img)




        if cv2.waitKey(10) == 27:
            break
        elif cv2.waitKey(10) == ord('c'):
            print imgHSV[c,a]

def dimension_converter(cx,cy):
    x=((camx-camxl)/2)
    y=((camy-camyl)/2)
    if(cx>x):
        cx = cx-x
    else:
        cx=1
    if(cy>y):
        cy = cy-y
    else:
        cy = 1
    return cx,cy



        # if(len(conts)==2):
        #     if(pinchFlag == 1):
        #         pinchFlag = 0
        #         mouse.release(Button.left)
        #         print("release")
        #
        #     x1,y1,w1,h1 = cv2.boundingRect(conts[0])
        #     x2,y2,w2,h2 = cv2.boundingRect(conts[1])
        #     cv2.rectangle(img,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
        #     cv2.rectangle(img,(x2,y2),(x2+w2,y2+h2),(255,0,0),2)
        #     cx1 = x1+w1/2
        #     cy1 = y1+h1/2
        #     cx2 = x2+w2/2
        #     cy2 = y2+h2/2
        #     cx = (cx1+cx2)/2
        #     cy = (cy1+cy2)/2
        #     if(cx>16):
        #         cx = cx-16
        #     else:
        #         cx=0
        #     if(cy>12):
        #         cy = cy-12
        #     else:
        #         cy = 0
        #
        #     cv2.line(img,(cx1,cy1),(cx2,cy2),(255,0,),2)
        #     cv2.circle(img,(cx,cy),2,(0,0,255),2)
        #     mouseLoc = mLocOld+((cx,cy)-mLocOld)/DampingFactor
        #     mouse.position=(sx-(mouseLoc[0]*sx/camxl),mouseLoc[1]*sy/camyl)
        #     while mouse.position!=(sx-(mouseLoc[0]*sx/camxl),mouseLoc[1]*sy/camyl):
        #         pass
        #     mLocOld = mouseLoc
        #
        #
        # elif(len(conts)==1):
        #     if(pinchFlag == 0):
        #         mouse.press(Button.left)
        #         pinchFlag=1
        #         print("mouse press")
        #     x,y,w,h = cv2.boundingRect(conts[0])
        #     cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        #     cx = x+w/2
        #     cy = y+h/2
        #     if(cx>16):
        #         cx = cx-16
        #     else:
        #         cx=0
        #     if(cy>12):
        #         cy = cy-12
        #     else:
        #         cy = 0
        #     cv2.circle(img,(cx,cy),(w+h)/4,(0,0,255),2)
        #     mouseLoc = mLocOld+((cx,cy)-mLocOld)/DampingFactor
        #     mouse.position=(sx-(mouseLoc[0]*sx/camxl),mouseLoc[1]*sy/camyl)
        #     while mouse.position!=(sx-(mouseLoc[0]*sx/camxl),mouseLoc[1]*sy/camyl):
        #         pass
        #     mLocOld = mouseLoc










