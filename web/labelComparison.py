import time
import os
import time
import yaml
from itertools import repeat
from applicationsConstants import *
from concurrent.futures import ThreadPoolExecutor
from helper import doAuthentication, createLocalDirectory
from utils import generateImageFromBase64LabelStream, is_valid_PNG_base64_image, makeNewDirInDrive, printColoured, uploadFileInDrive, strToDict

class LabelComparison():
    """ class to generate labels for LineByLineLabelComparisonResult file """
     
    def __init__(self, startTime, labelOnDrive, comparisonResultDataList, labelary):
        """ Constructor for LabelComparison. """
        self.startTime = startTime
        self.labelOnDrive = labelOnDrive
        self.doAuthenticationIfrequired()
        self.setupOutputFolders()
        self.containerIdtoShipmethodDict = dict()
        self.comparisonResultDataList = comparisonResultDataList
        print(len(self.comparisonResultDataList), "length", type(self.comparisonResultDataList))
        self.labelary = labelary
     
    def doAuthenticationIfrequired(self):
        """ Method use to authenticate the user. """
        if self.labelOnDrive:
            doAuthentication()
     
    def setupOutputFolders(self):
        """
        Method use to set up the output folders for expected labels and actual labels.
        If user have choosen labelOnDrive as true than it will setup the folders on drive else on local machine.
        """
        createLocalDirectory(EXPECTED_LABELS_DIR_NAME)
        createLocalDirectory(ACTUAL_LABELS_DIR_NAME)
        if self.labelOnDrive:
            self.expectedLabelsOutputFolder = f'{EXPECTED_LABEL_DRIVE_FOLDER}{self.startTime}/'
            self.actualLabelsOutputFolder = f'{ACTUAL_LABEL_DRIVE_FOLDER}{self.startTime}/'
            makeNewDirInDrive(COMPARISON_RESULT_DRIVE_FOLDER)
            makeNewDirInDrive(self.expectedLabelsOutputFolder)
            makeNewDirInDrive(self.actualLabelsOutputFolder)
        else:
            self.expectedLabelsOutputFolder = EXPECTED_LABEL_LOCAL_FOLDER
            self.actualLabelsOutputFolder = ACTUAL_LABEL_LOCAL_FOLDER
     
    def outputLabelFolder(self, labelStreamKey):
        if labelStreamKey == "expectedStream":
            return self.expectedLabelsOutputFolder
        return self.actualLabelsOutputFolder
     
    def getOutputImageLocalPath(self, containerId, labelStreamKey):
        imageExtension = "pdf" if (self.containerIdtoShipmethodDict[containerId]["labelType"] == ZPL_LABEL_TYPE and \
            self.labelary.labelType == PDF_LABEL_TYPE) else "jpg"
        if labelStreamKey == "expectedStream":
            return  f'{EXPECTED_LABEL_LOCAL_FOLDER}/{containerId}.{imageExtension}'
        return  f'{ACTUAL_LABEL_LOCAL_FOLDER}/{containerId}.{imageExtension}'
 
    def generateLabel(self, comparisonResult):
        comparisonResult = comparisonResult.strip().strip("\n")
        expectedLabelStreamKey = "expectedStream"
        actualLabelStreamKey = "actualStream"
        comparisonResulOutputJson = strToDict(comparisonResult)
        containerId = ""
        base64LabelStream = comparisonResulOutputJson[expectedLabelStreamKey]

        if comparisonResulOutputJson["differences"] != "null":
            # ToDo: Logic of loading each comparisonResult can be better.
            # ToDo: Make report format better so that we can load it fast as json object.
            labelType = ZPL_LABEL_TYPE
        else:
            if is_valid_PNG_base64_image(base64LabelStream, containerId):
                labelType = PNG_LABEL_TYPE
            else:
                labelType = PDF_LABEL_TYPE
                #Todo Enhance logic to show PDF Diff
                return

        if "containerIdentifier" in comparisonResulOutputJson.keys():
            containerId = comparisonResulOutputJson["containerIdentifier"].strip("\'")
        containerPayload = containerId[:]
        if len(containerId) > 29:
            containerId = "Payload" + str(int(time.time() * 10**6))
        if "containerId" in comparisonResulOutputJson.keys():
            containerId = comparisonResulOutputJson["containerId"]
        elif "containerPayload" in comparisonResulOutputJson.keys():
            containerId = "Payload" + str(int(time.time() * 10**6))
            containerPayload = comparisonResulOutputJson["containerPayload"]
        self.containerIdtoShipmethodDict[containerId] = dict()
        self.containerIdtoShipmethodDict[containerId] = {"labelId": comparisonResulOutputJson["labelId"], "labelType": labelType, "containerPayload": containerPayload}
        outputImagePathExpected = self.getOutputImageLocalPath(containerId, expectedLabelStreamKey)
        outputImagePathActual = self.getOutputImageLocalPath(containerId, actualLabelStreamKey)
        printColoured(f'[INFO]: Generating label image for {expectedLabelStreamKey} of {containerId}', "green")
        generateImageFromBase64LabelStream(base64LabelStream, outputImagePathExpected, labelType, self.labelary)
        printColoured(f'[INFO]: Generating label image for {actualLabelStreamKey} of {containerId}', "green")
        base64LabelStream = comparisonResulOutputJson[actualLabelStreamKey]
        generateImageFromBase64LabelStream(base64LabelStream, outputImagePathActual, labelType, self.labelary)
        
    def generateLabelsForLabelComparisonResult(self):
        with ThreadPoolExecutor(GENERATE_LABEL_WORKERS) as executor:
            executor.map(self.generateLabel, self.comparisonResultDataList)
     
    def processUploadLabel(self, containerId, labelStreamKey):
        outputImagePath = self.getOutputImageLocalPath(containerId, labelStreamKey)
        if os.path.exists(outputImagePath):
            printColoured(f"[INFO]: Uploading label generated from {labelStreamKey} of {containerId} on drive", "green")
            uploadFileInDrive(outputImagePath, self.outputLabelFolder(labelStreamKey))
     
    def uploadLabels(self, labelStreamKey):
        if self.labelOnDrive:
            with ThreadPoolExecutor(UPLOADING_LABEL_WORKERS) as executor:
                executor.map(self.processUploadLabel, list(self.containerIdtoShipmethodDict), repeat(labelStreamKey))