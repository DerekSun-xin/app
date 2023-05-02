from flask import Flask,render_template,request,redirect,jsonify
import os
import re


from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

import string
import json

'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = "1a780756dae54b4b8fb26492ab5a9c44"
endpoint = "https://mycognitiveservicesresourcexinsun.cognitiveservices.azure.com/"

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World"

@app.route("/about")
def about():
    return  "<h1 style='color:red'>About!!</h1>"

app.config["IMAGE_UPLOADS"]="/Users/sunxin/Desktop/app/static/img/uploads"

@app.route("/upload-image",methods=["GET","POST"])
def upload_image():

    if request.method=="POST":

        if request.files:
            image=request.files["image"] #image is the name
            #print(type(image))
            read_response = computervision_client.read_in_stream(image, raw=True)
            # Get the operation location (URL with ID as last appendage)
            read_operation_location = read_response.headers["Operation-Location"]
            # Take the ID off and use to get results
            operation_id = read_operation_location.split("/")[-1]

             # Call the "GET" API and wait for the retrieval of the results
            while True:
                read_result = computervision_client.get_read_result(operation_id)
                if read_result.status.lower () not in ['notstarted', 'running']:
                    break
                print ('Waiting for result...')
                time.sleep(10)
            
            combine = ""
            # Print the detected text, line by line
            if read_result.status == OperationStatusCodes.succeeded:
                for text_result in read_result.analyze_result.read_results:
                    for line in text_result.lines:
                
                        #matchObj = re.match()
                        #print(line.text)
                        combine+=line.text
                        #print(line.bounding_box)
            print()
            
            #info get rid of variable combine's whitespaces and newline characters
            info = combine.translate({ord(c): None for c in string.whitespace})

            #Get rid of info's punctuation
            info = re.sub(r'[^\w\s]', '', info)
            print(info)
            
            #Build a dictionary thisDict to store ID info
            ID = {"姓名":"","性别":"","民族":"","出生":"","住址":"","公民身份号码":""}
            
            #store ID info in var ID(type/dict)
            if(info.find("姓名")!=-1 and info.find("性别")!=-1):
                a = info.find("姓名")
                b = info.find("性别")
            # print(info[a+2:b])
                ID["姓名"]=info[a+2:b]
            
            if(info.find("性别")!=-1 and info.find("民族")!=-1):
                a = info.find("性别")
                b = info.find("民族")
                #print(info[a+2:b])
                ID["性别"]=info[a+2:b]
            
            if(info.find("民族")!=-1 and info.find("出生")!=-1):
                a = info.find("民族")
                b = info.find("出生")
                #print(info[a+2:b])
                ID["民族"]=info[a+2:b]
                
            if(info.find("出生")!=-1 and info.find("住址")!=-1):
                a = info.find("出生")
                b = info.find("住址")
                #print(info[a+2:b])
                ID["出生"]=info[a+2:b]
            
            if(info.find("住址")!=-1 and info.find("公民身份号码")!=-1):
                a = info.find("住址")
                b = info.find("公民身份号码")
                #print(info[a+2:b])
                ID["住址"]=info[a+2:b]
                
            if(info.find("公民身份号码")!=-1):
                a = info.find("公民身份号码")
                #print(info[a+6:])
                ID["公民身份号码"]=info[a+6:]
            
            #print(ID) #type:dict
            #print()
            
            data=json.dumps(ID,ensure_ascii=False)
            
            print(data,type(data))
            #image.save(os.path.join(app.config["IMAGE_UPLOADS"],image.filename))
            #print("image saved")
            #print(image)
            
            #return redirect(request.url)
            return showInfo(ID)
            #return showInfo(data)
       
    return render_template("public/upload_image.html")

@app.route("/upload-image",methods=["GET","POST"])
def showInfo(ID):
    name=ID["姓名"]
    sex=ID["性别"]
    nation=ID["民族"]
    birth=ID["出生"]
    address=ID["住址"]
    IDNumber=ID["公民身份号码"]
    return render_template("public/upload_image.html",myName=name,mySex=sex,myNation=nation,myBirth=birth,myAddress=address,myIDNumber=IDNumber)


#space
if(__name__=="__main__"):
    app.run()
