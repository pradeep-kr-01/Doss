import cv2
from cvzone.HandTrackingModule import HandDetector

def launch_instance():
    import boto3
    ec2 = boto3.client("ec2")
    info = ec2.run_instances(
        ImageId='ami-0d63de463e6604d0a',
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1)
    return info

model = HandDetector()
cap=cv2.VideoCapture(0)
while True:   
    status,photo=cap.read()
    hand=model.findHands(photo)
    cv2.imshow("hii",photo)
    if cv2.waitKey(50) ==13:
        break
    lmlist=hand[0]
#     print(lmlist)
    if lmlist:
        count = 0
        fingeruplist = []
        for i in lmlist:
            fingeruplist+=model.fingersUp(i)

        count = sum(fingeruplist)   
        # print(count)
        for i in range(count):
            print(launch_instance())
            print(f"{count} Instance launched")
        break

cap.release()
cv2.destroyAllWindows()