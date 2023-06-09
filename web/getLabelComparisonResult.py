import sys
import os
import time
import getpass
import urllib3
import xlsxwriter
import argparse
from labelary import Labelary
from utils import printColoured
from applicationsConstants import *
from labelComparison import LabelComparison
from MachineLearning import classify
     
urllib3.disable_warnings()
sys.dont_write_bytecode = True
     
parser = argparse.ArgumentParser()
startTime = str(int(time.time()))
excelFileName = f'labelcomparator_{startTime}.xlsx'
comparisonResultBaseUrl = f'{AMAZON_DRIVE_BASE_URL}documents/{getpass.getuser()}@/'
     
def readComparisonResultFile(comparisonResultFilePath):
    comparisonResultFile = open(comparisonResultFilePath, "r").read()
    comparisonResultFileDataList = comparisonResultFile.strip().split("LabelComparisonOutput")
    if comparisonResultFileDataList[0].strip() == "Persisting first 5000 (max) label comparison failures ->":
        comparisonResultFileDataList.pop(0)
    if not comparisonResultFileDataList[0]:
        comparisonResultFileDataList.pop(0)
    return comparisonResultFileDataList
     
def generateURL(labelComparison, labelStreamKey, containerId):
    labelURL = f'{labelComparison.outputLabelFolder(labelStreamKey)}{containerId}.jpg'
    if labelComparison.containerIdtoShipmethodDict[containerId]["labelType"] == ZPL_LABEL_TYPE and \
        labelComparison.labelary.labelType == PDF_LABEL_TYPE:
        labelURL = f'{labelComparison.outputLabelFolder(labelStreamKey)}{containerId}.pdf'
    if labelComparison.labelOnDrive:
        labelURL = f'{comparisonResultBaseUrl}{labelURL}'
    return labelURL
     
def createWorkbook(labelComparison):
    workbook = xlsxwriter.Workbook(excelFileName)
    worksheet = workbook.add_worksheet()
    headerFormat = workbook.add_format({
        'bold': True,
        'border': 3,
        'fg_color': '3DD4F5',
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 20,
        'text_wrap': True
    })
    rowFormat = workbook.add_format({
        'border':   3,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 20,
        'text_wrap': True
    })
    imageProperties = {'x_scale': 0.5, 'y_scale': 0.5, 'x_offset': 15, 'y_offset': 10}
    worksheetHeader = ["containerID", "shipmethod", "Label Type", "Expected Label", "Actual Label", "container Payload","ML Pred"]
    worksheet.set_column('A:C', 35)
    worksheet.set_column('D:E', 90) # 90 -> Image Width
    worksheet.write_row(0, 0, worksheetHeader, headerFormat)
    worksheet.set_row(0, 30)
    for index, containerId in enumerate(labelComparison.containerIdtoShipmethodDict):
        expectedLabelURL = generateURL(labelComparison, "expectedStream", containerId)
        actualLabelURL = generateURL(labelComparison, "actualStream", containerId)
        worksheet.set_row(index + 1, 750, rowFormat) # 750 -> Image Height
        worksheet.write(index + 1, 0,  containerId)
        worksheet.write(index + 1, 1,  labelComparison.containerIdtoShipmethodDict[containerId]["labelId"])
        worksheet.write(index + 1, 2, labelComparison.containerIdtoShipmethodDict[containerId]["labelType"])
        worksheet.insert_image(index + 1, 3, expectedLabelURL, imageProperties)
        worksheet.insert_image(index + 1, 4, actualLabelURL, imageProperties)
        worksheet.write(index + 1, 5, labelComparison.containerIdtoShipmethodDict[containerId]["containerPayload"])
        classifier = classify(labelComparison.containerIdtoShipmethodDict[containerId]["labelType"],containerId)
        worksheet.write(index + 1,6, classifier.get_prediction()) ## get classification
    workbook.close()
     
if __name__ == "__main__":
    parser.add_argument("--file", type=str, help="Absolute file path of label comparison results file", required=True)
    parser.add_argument("--dpmm", type=int, default=12, help="DPI of ZPL label")
    parser.add_argument("--width", type=int, default=4, help="Width of ZPL label")
    parser.add_argument("--height", type=int, default=6, help="Height of ZPL label")
    parser.add_argument("--zplLabelFormat", type=str, default="PNG", help="Label format of ZPL labels")
    parser.add_argument("--labelOnDrive", type=bool, default=False, help="Where do you want to compare \
    labels? Local system works significantly fast in comparison of drive. If you choose drive, it will take at least 2 second \
            to generate and upload each label to the drive.")
    parser.add_argument("--region", type=str, default=None, help="Region for label comparison results file")
    args = parser.parse_args()
    labelary = Labelary(args.dpmm, f'{args.width}x{args.height}', args.zplLabelFormat, args.region)
    comparisonResultDataList = readComparisonResultFile(args.file.strip())
    printColoured(f"\nHello, {getpass.getuser()}", "green")
    printColoured(f'[INFO]: The total number of results available are: {len(comparisonResultDataList)}', "green")
    labelComparison = LabelComparison(startTime, args.labelOnDrive, comparisonResultDataList, labelary)
    labelComparison.generateLabelsForLabelComparisonResult()
    labelComparison.uploadLabels("expectedStream")
    labelComparison.uploadLabels("actualStream")
    createWorkbook(labelComparison)
    printColoured(f'[INFO]: workbook created with name {excelFileName}', "green")