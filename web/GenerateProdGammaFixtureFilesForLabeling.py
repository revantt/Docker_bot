import json
import os
import sys
import time
import getpass
import urllib3
from utils import printColoured
from utils import getPrintableTable
from authentication import Authentication
from shorttermutils import *
from utils import *
from temporaryUtils import *
from GenerateGammaContainers import *

urllib3.disable_warnings()
user = getpass.getuser()
serviceName = input("Service for which you want to run regression. Enter TLGS or NGLS: ")
if serviceName == "NGLS":
    api = "getSelfServeLabelByIdInput"
else:
    api = "getLabelByIdInput"
inputProdRegressionFilePath = input("Enter the path to read existing prod regression input: ")
prodRegressionInputFile = open(inputProdRegressionFilePath, "r")
# Regression Files may contain duplicate records, hence storing the
# unique requests in file inputFileWithoutDuplicates.txt. This file will be used for further processing.
inputFileWithoutDuplicates = open("../../inputFileWithoutDuplicates.txt", "r+")
try:
    inputFileWithoutDuplicates.truncate(0)
    lines = prodRegressionInputFile.readlines();
    prod_tcda_containers_id_list = []
    for line in lines:
        obj = json.loads(line)
        if obj[api]["containerId"] not in prod_tcda_containers_id_list:
            prod_tcda_containers_id_list.append(obj[api]["containerId"])
            inputFileWithoutDuplicates.write(json.dumps(obj) + '\n')
finally:
    prodRegressionInputFile.close()
    inputFileWithoutDuplicates.close()

if __name__ == "__main__":
    user = getpass.getuser()
    printColoured(f"\nHello, you logged in as  {user}", "green")
    printColoured(f"[INFO]: Authentication going on for user {user} ...", "green")
    auth = Authentication()
    auth.sentryAuthentication()
    printColoured("[INFO]: Sentry authentication done !!", "green")
    auth.midwayAuthentication()
    printColoured("[INFO]: Midway authentication done !!", "green")
    session = auth.session
    region = input("Enter region : ")
    if region not in ["EU", "NA", "FE"]:
        print("Enter a correct region from ", ["EU", "NA", "FE"])
    session = auth.session
    gammaContainerGeneratorObject = GammaContainerGenerator(region, session)
    prodToGammaTCDAContainerMapping = gammaContainerGeneratorObject.generateProdToGammaTCDAContainersMapping(
        prod_tcda_containers_id_list)
    gamma_tcda_containers_id_list = list(map(lambda value: value, prodToGammaTCDAContainerMapping.values()))
    printColoured(f"\nGenerating output files with prod and corresponding gamma fixture", "green")
    prodRegressionInputFileWithoutDuplicates = open("../../inputFileWithoutDuplicates.txt", "r")
    RegressionOutPutFolder = "/Users/" + user + "/Desktop/Output";
    ProdRegressionFilePath = RegressionOutPutFolder + "/Prod.txt"
    GammaRegressionFilePath = RegressionOutPutFolder + "/Gamma.txt"
    dirIsExist = os.path.exists(RegressionOutPutFolder)
    fileExists = os.path.exists(ProdRegressionFilePath)
    fileExists2 = os.path.exists(GammaRegressionFilePath)
    if not dirIsExist:
        os.makedirs(RegressionOutPutFolder)
    if fileExists:
        os.remove(ProdRegressionFilePath)
        ProdRegressionOutputFile = open(ProdRegressionFilePath, "w")
    else:
        ProdRegressionOutputFile = open(ProdRegressionFilePath, "w")
    if fileExists2:
        os.remove(GammaRegressionFilePath)
        GammaRegressionOutputFile = open(GammaRegressionFilePath, "w")
    else:
        GammaRegressionOutputFile = open(GammaRegressionFilePath, "w")
    lines = prodRegressionInputFileWithoutDuplicates.readlines()
    recordIndex = 0
    try:
        for line in lines:
            obj = json.loads(line)
            if gamma_tcda_containers_id_list[recordIndex] != "Error":
                ProdRegressionOutputFile.write(json.dumps(obj) + '\n')
                obj[api]["containerId"] = gamma_tcda_containers_id_list[recordIndex]
                GammaRegressionOutputFile.write(json.dumps(obj) + '\n')
        recordIndex = recordIndex + 1
    finally:
        GammaRegressionOutputFile.close()
        ProdRegressionOutputFile.close()
        prodRegressionInputFileWithoutDuplicates.close()
    printColoured(f"\nResults stored in " + ProdRegressionFilePath + " and " + GammaRegressionFilePath, "green")
