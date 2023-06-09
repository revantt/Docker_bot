import json
import yaml
import base64
import subprocess
import httpRequest
from termcolor import colored
from tabulate import tabulate
from bs4 import BeautifulSoup
from collections import defaultdict
from collections import OrderedDict
import applicationsConstants as ApplicationsConstants
import base64
import io
from PIL import Image

"""
# Method use to beautify the HTML string using BeautifulSoup.
# @param rawHTML: raw html which needs to beautify.
# @param parser: specifies which parser needs to use.
# @return BeautifulSoup object which consists of rawHTML.
"""
def getBeautifyHTML(rawHTML, parser="html.parser"):
    return BeautifulSoup(rawHTML, parser)
     
def strToDict(input):
    inputString = str(input)
    resultDict = {}
    eachCharacter = ""
    flag = 0
    key = []
    value = []
    if inputString.startswith("{") and inputString.endswith("}"):
        inputString = inputString[1 : len(inputString) - 1]
        for i in range(len(inputString)):
            eachCharacter = inputString[i]
            if eachCharacter != " " or eachCharacter != "'":
                if eachCharacter == ",":
                    keyString = "".join(key).strip().strip("\'")
                    valueString = "".join(value).strip().strip("\'")
                    resultDict[keyString] = valueString
                    key = []
                    value = []
                    flag = 0
                elif eachCharacter == ":":
                    flag = 1
                else:
                    if flag == 1:
                        value.append(eachCharacter)
                    else:
                        key.append(eachCharacter)
        if key:
            keyString = "".join(key).strip().strip("\'")
            valueString = "".join(value).strip().strip("\'")
            resultDict[keyString] = valueString
        return resultDict
    return "Not valid JSON"
     
def convert2json(data):
    """
    Method use to convert json type string into json type object.
    If data is equal to empty string make data='{"ok": false}'.
    Parameters
    ----------
    data: json type str
        Json type string which needs to be load using json.
     
    Returns
    -------json
    Json type object.
    """
    data = data.strip()
    if data == ApplicationsConstants.EMPTY_STRING:
        data = '{"ok": false}'
    try:
        return json.loads(data)
    except json.decoder.JSONDecodeError:
        return {"ok":True, "data": data}
     
def loadyaml(data, Loader=yaml.FullLoader):
    """
    Method use to load yaml type string.
     
    Parameters
    ----------
    data: yaml type str
        Yaml type string which needs to be load using yaml.
    Loader: yaml Loader object (optional)
        Loader which specifies how to treat yaml type string.
        If not given default value used yaml.FullLoader
     
    Returns
    -------
    yaml
    Yaml type object.
    """
    return yaml.safe_load(data)
     
def getPrintableTable(data, headers, tablefmt='orgtbl'):
    """
    Method use to print data into beautify table.
     
    Parameters
    ----------
    data: list
        Data which needs to be print like table.
    headers: list
        Headers of table.
    tablefmt: str(optional)
        Table format use to print table.
        If not given default value used 'orgtbl'
     
    Returns
    -------
    tabulate table
        Tabulate type object which is beautify table.
    """
    table = tabulate(data, headers=headers, tablefmt=tablefmt)
    return table
     
def printColoured(data, color):
    """
    Method use to print data in colored format.
     
    Parameters
    ----------
    data: str
        Data which needs to be print in some color.
    color: str
    Color in which data needs to print.
    """
    print(colored(data, color))
     
def makeNewDirInDrive(foldername):
    subprocess.run(["drive", "mkdir", foldername])
    printColoured(f"[Info]: Created new directory on drive {foldername}", "green")
     
def uploadFileInDrive(filename, foldername):
    subprocess.run(["drive", "upload", filename, foldername])
     
def getFileLocationFromPackage(session, packageName, branchName, fileName):
    """
    Method use to get location of file fileName in particular package and in particular branch.
    If package contains multiple files with same name it will return all location as list.
     
    Parameters
    ----------
    packageName: str
        Name of the package where file exist.
    branchName: str
        Name of the branch where file exist in package.
    fileName: str
        Name of the file for which location needs to find.
     
    Returns
    -------
    fileLocation: list
        Location of the file fileName in the package packageName for branch branchName.
    """
    url = f"https://code.amazon.com/packages/{packageName}/commits/{branchName}/autocomplete_file_name?term={fileName}"
    fileLocation = httpRequest.HttpRequest(session, url).getRequestResponse("GET")
    return fileLocation
     
def getFileDataFromPackage(session, packageName, branchName, fileLocation):
    """
    Method use to get data of a file from particular package and from particular branch using
    the given file location.
     
    Parameters
    ----------
    packageName: str
        Name of the package where file exist.
    branchName: str
        Name of the branch where file exist in package.
    fileLocation: str
        Location of the file in the package packageName and branch branchName.
     
    Returns
    -------
    fileData: str
        Data of the file for given flieLocation in the package packageName and branch branchName.
    """
    url = f"https://code.amazon.com/packages/{packageName}/blobs/{branchName}/--/{fileLocation}?raw=1"
    fileData = httpRequest.HttpRequest(session, url).getRequestResponse("GET")
    return fileData["data"]
     
def mergeDictsIntoDict(dictList, mergekey):
    """
    Method use to merge multiple dictionaries into one dictionary. If given multiple dictionaries
    contains same key and have different data it will merge them as seperate dictionary with key as
    respective mergekey and than mapped to same key in transformed dict.
    Ex: <common_key_in_multiple_dictionaries>: {<mergekey1>:<data1>, <mergekey2>:<data2>, <mergekey3>:<data3>}
     
    Parameters
    ----------
    dictList: list
        List contains multiple dictionaries.
    mergekey: str
        Key that use to merge multiple dictionaries list if conflict occurs.
     
    Returns
    -------
    transformedDict: dict
        Dictionary which contains all of the keys from multiple given dictionaries.
    """
    transformedDict = defaultdict(dict)
    for dict_ in dictList:
        for key, value in dict_.items():
            if type(value) == OrderedDict:
                continue
            transformedDict[key].update({dict_[mergekey]:value})
    transformedDict = dict(transformedDict)
    for key in transformedDict:
        values = set(transformedDict[key].values())
        if len(values) == 1:
            transformedDict[key] = values.pop()
    return transformedDict
     
def convertBase64toImage(base64DecodedData, outputImagePath):
    with open(outputImagePath, 'wb') as outputFile:
        outputFile.write(base64DecodedData)
     
def generateImageFromBase64LabelStream(base64LabelStream, outputImagePath, labelType, labelary):
    base64DecodedData = base64.b64decode(base64LabelStream)
    if labelType == ApplicationsConstants.ZPL_LABEL_TYPE:
        labelary.generateLabelFromZplStream(base64DecodedData, labelType, outputImagePath)
    else:
        convertBase64toImage(base64DecodedData, outputImagePath)

def is_valid_PNG_base64_image(image_string, containerId):
    # checking valid base64 image string
    try:
        image = base64.b64decode(image_string)
        with Image.open(io.BytesIO(image)) as img:
            return True
    except Exception:
        printColoured(f'[WARN]: PDF Format found containerId : {containerId}', "yellow")
        return False