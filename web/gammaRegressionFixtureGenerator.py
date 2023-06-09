import json
import getpass

import urllib3
from utils import printColoured
from utils import convert2json
from httpRequest import HttpRequest
import applicationsConstants as ApplicationsConstants
import applicationsMapConstants as ApplicationsMapConstants
from authentication import Authentication
import applicationsMapConstants

'''
This class is used for generating gamma fixtures.
'''


def generateGammaFixture(session, prodFixture):
    taxonomyResponse = ApplicationsConstants.EMPTY_STRING
    prodFixtureDict = json.loads(prodFixture)
    # print(prodFixtureDict)
    prodContainerId = prodFixtureDict["getSelfServeLabelByIdInput"]['containerId']
    prodOrg = prodFixtureDict["getSelfServeLabelByIdInput"]["labelProperties"]["displayOrg"]
    prodRealm = ""
    if prodOrg in applicationsMapConstants.EU_REGION_CODE:
        prodRealm = "EU"
    elif prodOrg in applicationsMapConstants.NA_REGION_CODE:
        prodRealm = "NA"
    elif prodOrg in applicationsMapConstants.FE_REGION_CODE:
        prodRealm = "FE"
    else:
        prodRealm = "CN"
    url = ApplicationsMapConstants.TAXONOMY_URL[prodRealm]
    copyContainerUrl = url + "copyContainer"
    data = json.dumps({"containerId": prodContainerId})
    # requestResponse = HttpRequest(session, copyContainerUrl, data, ApplicationsMapConstants.TCDA_HEADERS).getRequestResponse("POST")
    cookies = dict(session.cookies.items())
    try:
        taxonomyResponse = HttpRequest(session, copyContainerUrl, data, ApplicationsMapConstants.TCDA_HEADERS, cookies).getRequestResponse("POST")
    except:
        taxonomyResponse = {}
    # print(taxonomyResponse)
    gammaContainerId = ""
    if "SUCCESS" in taxonomyResponse:
        print("SUCCESS")
        gammaContainerId = taxonomyResponse["SUCCESS"]
    elif "ERROR" in taxonomyResponse:
        print(taxonomyResponse["ERROR"])
        loadContainerUrl = url + "loadContainer?containerId=" + prodContainerId + "&versionNumber="
        # requestResponse = HttpRequest(session, loadContainerUrl, data, ApplicationsMapConstants.TCDA_HEADERS).getRequestResponse("GET")
        cookies = dict(session.cookies.items())
        try:
            taxonomyResponse = HttpRequest(session, loadContainerUrl, data, ApplicationsMapConstants.TCDA_HEADERS, cookies).getRequestResponse("GET")
            responseData = taxonomyResponse['data']
            trackingId = extractTrackingId(responseData)
            # print(trackingId)
            gammaTrackingIdUrl = ApplicationsMapConstants.TAXONOMY_GAMMA_URL[prodRealm] + "visualizeTCDAData?select_feature=Load&indexName=TrackingId&indexValue=" + trackingId + "&versionNumber="
            taxonomyResponse = HttpRequest(session, gammaTrackingIdUrl, data, ApplicationsMapConstants.TCDA_HEADERS, cookies).getRequestResponse("GET")
            gammaContainerId = extractContainerId(taxonomyResponse['data'])
        except:
            gammaContainerId = ""
    gammaFixture = prodFixture.replace(prodContainerId, gammaContainerId)
    return gammaContainerId, prodContainerId, gammaFixture
    

def extractContainerId(data):
    try:
        ind = data.index("containerId=") + 12
        return data[ind : ind + 29]
    except:

        print("Exceptio:", data)
        return ""

def extractTrackingId(data):
    arr = data.split("\n")
    flag = 0
    trackingId = ""
    for i in range(len(arr)):
        if "trackingId" in arr[i]:
            flag = 1
        elif flag == 1 and "cellContent" in arr[i]:
            flag = 2
        elif flag == 2:
            if len(arr[i].strip()) != 0:
                trackingId = arr[i].strip()
                return trackingId
    return trackingId

# def copyProdContainerToGammaContainer(self, session, prodContainerTCDAId):
#     url = self.url + "copyContainer"
#     data = json.dumps({"containerId": prodContainerTCDAId})
#     if self.cookies == ApplicationsConstants.EMPTY_STRING:
#         requestResponse = HttpRequest(session, url, data, ApplicationsMapConstants.TCDA_HEADERS).getRequestResponse("POST")
#         self.cookies = dict(session.cookies.items())
#     taxonomyResponse = HttpRequest(session, url, data, ApplicationsMapConstants.TCDA_HEADERS, self.cookies).getRequestResponse("POST")
#     return taxonomyResponse

if __name__ == "__main__":
    printColoured(f"\nHello, you logged in as  {getpass.getuser()}", "green")
    printColoured(f"[INFO]: Authentication going on for user {getpass.getuser()} ...", "green")
    auth = Authentication(maxRedirects=20)
    auth.sentryAuthentication()
    printColoured("[INFO]: Sentry authentication done !!", "green")
    auth.midwayAuthentication()
    printColoured("[INFO]: Midway authentication done !!", "green")
    region = input("Enter region : ")
    if region not in ["EU", "NA", "NRT"]:
        print("Enter a correct region from ", ["EU", "NA", "NRT"])
    session = auth.session
    file = open('prodRegressionFixture.txt', "r")
    fixtures = file.readlines()
    urllib3.disable_warnings()
    gammaToProdDict = {}
    gammaFixtures = []
    gammaToProdString = ""
    for fixture in fixtures:
        gammaContainer, prodContainer, gammaFixture = generateGammaFixture(session,fixture)
        gammaToProdDict[prodContainer] = gammaContainer
        gammaToProdString += prodContainer + "," + gammaContainer +"\n"
        gammaFixtures.append(gammaFixture)

    jsonObject = json.dumps(gammaToProdDict, indent = 4)
    with open("gammaContainerToProdContainerMap.json", "w") as outfile:
        outfile.write(jsonObject)

    with open("gammaToProd-" + region + ".txt", "w") as outfile:
        outfile.write(gammaToProdString)
    
    with open("gammaFixtures.txt", "w") as outfile:
        for gammaFixture in gammaFixtures:
            outfile.write(gammaFixture + "\n")