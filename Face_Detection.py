import numpy as np  
import cv2  
  
def face_detect(img):  
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray,1.1,5,cv2.CASCADE_SCALE_IMAGE,(50,50),(100,100))  
    if(len(faces) > 0):
        print("CATCH!")
    else :
        print("NOT YET!")
    for faceRect in faces:  
        x,y,w,h = faceRect
        color=[255,0,0]
        img[y:y+5,x:x+w]=color
        img[y+h:y+h+5,x:x+w]=color
        img[y:y+h,x:x+5]=color
        img[y:y+h,x+w:x+w+5]=color
        cv2.rectangle(img.astype(np.int32),(x,y),(x+w,y+h),(255,0,0),2,8,0)  
    
        roi_gray = gray[y:y+h,x:x+w] 
        roi_color = img[y:y+h,x:x+w]  
    return img
    
  
# img = cv2.imread("12644633_574341129379918_6543906287908249817_n.jpg") 
# img, roi_gray, roi_color = face_detect(img)
# print(roi_gray.shape)
# cv2.imshow("img",img)  
# cv2.waitKey (0)  
# cv2.destroyAllWindows()  