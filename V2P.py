import cv2
import re
from moviepy.editor import VideoFileClip
import os
import optparse
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import numpy as np
import time
from reprint import output

#parsing constructor
parser = optparse.OptionParser()
parser.add_option('-v', '--video',
    action="store", dest="VideoName",
    help="Name of the Video File", default="")
#========================================
#--> The video number here is to avoid mixing of images. So in case if you are converting multiple videos to PDF which are in the "same folder" then give different Video number so that the images are easily differentiated. In case if you are only convreting only "one video" at a time then give the number as just "1"
#========================================
parser.add_option('-n', '--Video Number',
    action="store", dest="VideoNum",
    help="Number of the Video File", default="")
parser.add_option('-s', '--Skip Seconds',
    action="store", dest="skip_sec",
    help="Jump the video by n seconds", default="")    
options, args = parser.parse_args()

skip_seconds = options.skip_sec             #parsing skip seconds from the args
Video_Num = options.VideoNum                #parsing the video file number from the args
Video_Name = options.VideoName              #parsing the video file name from the args
clip = VideoFileClip(Video_Name)                #feeding the name to the moviepy module to check the duration
vduration = clip.duration                   #getting the duration

print("\n" + "="*50)
print("AiMi-V2P: Video to PDF Converter")
print("="*50)

cap = cv2.VideoCapture(Video_Name)          #capturing the video with opencv
img_arr = []                                #array to store all the names of the image
slide_count = 0                             #total slides captured
comp_image = cv2.imread("test.jpg")         #an initial image to compare with 
comp_image = cv2.cvtColor(comp_image, cv2.COLOR_BGR2GRAY)   #converting it to grayscale

print("\n[+] CONVERSION IN PROCESS ...\n")

with output(output_type='dict') as output_lines:                #this line is for rewriting multiple lines
    for i in range(1,int(vduration), int(skip_seconds)):   
        status = ''
        check_point = i*1000                                    #converting secs to millisec
        cap.set(cv2.CAP_PROP_POS_MSEC,check_point)              # Go to the check_point sec. position
        ret,frame = cap.read()                                  # Retrieves the frame at the specified second
        cv2.imwrite(str(Video_Num) + "_" + str(i) + ".jpg", frame)  # Saves the frame as an image
        file_name = str(Video_Num) + "_" + str(i) + ".jpg"          #getting the file_name

        original = cv2.imread(str(Video_Num) + "_" + str(i) + ".jpg")   #reading the image for comparison
        original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)       #converting to grayscale
        s = ssim(comp_image, original)                              #calculating the ssim
        parameter = 0.9679829281775479                              #a parameter or threshhol used to compare image (editable)
        
        
        #running through the logics
        if s > parameter:
            os.remove(str(Video_Num) + "_" + str(i) + ".jpg")
            status = "REMOVED"                                      #removing if the file is identical   
     
        #if not identical, increasing the slide count, changing the comparing image to current image, appending the name to the list
        else:
            slide_count += 1
            comp_image = cv2.imread(str(Video_Num) + "_" + str(i) + ".jpg")
            comp_image = cv2.cvtColor(comp_image, cv2.COLOR_BGR2GRAY)
            img_arr.append(file_name)
            status = "UNIQUE SLIDE FOUND AND ADDED" 
        
        #just process output
        output_lines['         - Capturing frame Seq  '] = " {}".format(i)
        if i % 2 == 0:
            output_lines['         - Writing, Naming file '] = " [*]"
        else:
            output_lines['         - Writing, Naming file '] = " [ ]"
        if i % 2 == 0:
            output_lines['         - Comparing Files      '] = " [*]"
        else:
            output_lines['         - Comparing Files      '] = " [ ]"
        output_lines['         - Pixel Difference     '] = " {}".format(s)
        output_lines['         - Status               '] = " {}".format(status)
        output_lines['                   SLIDES '] = " {}".format(slide_count)
       

print("\n\n[+] Converting to PDF")                                  #PDF conversion    
command = ''        
for image in img_arr:                                               #creating a command with all image names
    command += ' ' + image
output = str(Video_Name) + ".pdf"                                   #output will be same of the video's name
output = output.replace(" ", "_")
print("[+] Creating PDF with " + str(slide_count) + " slides")
os.system('img2pdf ' + command  +  ' -o ' + output)
print("[+] Removing Images")
print("[+] Conversion Completed\n\n")

#removing the saved images
for image in img_arr:
    os.remove(image)