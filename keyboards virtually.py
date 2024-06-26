import cv2
import sys
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
finalText = ""

detector = HandDetector(detectionCon=0.8)
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
]

def drawAll(img, buttonList):
    imgNew = np.zeros_like(img, np.uint8)

    for button in buttonList:
        x, y = button.pos
        cvzone.cornerRect(imgNew, (button.pos[0], button.pos[1], button.size[0], button.size[1]), 20, rt=0)
        cv2.rectangle(imgNew, button.pos, (x + button.size[0], y + button.size[1]), (255, 0, 253), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 4)

    out = img.copy()
    alpha = 0.5
    mask = imgNew.astype(bool)
    out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
    return out

class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 5, 100 * i + 50], key))

while True:
    success, img = cap.read()
    if not success:
        break
    
    # Detect hands
    hands, img = detector.findHands(img)
    
    if hands:
        # Get the first hand's landmarks and bounding box
        hand = hands[0]
        lmList = hand['lmList']  # List of 21 landmark points
        bbox = hand['bbox']  # Bounding box info
        
        # Check if the index finger tip is over any button
        if lmList:
            for button in buttonList:
                x, y = button.pos
                w, h = button.size
                if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                    cv2.rectangle(img, button.pos, (x + w, y + h), (155, 0, 200), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    
                    l, _, _ = detector.findDistance(8, 12, img, draw=False)
                    if l < 45:
                        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 0), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        finalText += button.text
                        sleep(0.15)

    # Create rectangles for keys
    img = drawAll(img, buttonList)
    
    # Display the final text
    cv2.rectangle(img, (50, 350), (700, 450), (255, 255, 255), cv2.FILLED)
    cv2.putText(img, finalText, (60, 425), cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 0), 4)
    
    # Display the image
    cv2.imshow("IMAGE", img)
    
    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
