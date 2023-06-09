import json
from utils import convert2json
from httpRequest import HttpRequest
import applicationsConstants as ApplicationsConstants
import applicationsMapConstants as ApplicationsMapConstants

class Taxonomy:
    def __init__(self, carrierData):
        self.carrierData = carrierData
        self.cookies = ApplicationsConstants.EMPTY_STRING
        self.url = ApplicationsMapConstants.TAXONOMY_URL[carrierData.region]

    def generateGammaContainer(self, session, prodContainersTCDAId):
        taxonomyResponse = ApplicationsConstants.EMPTY_STRING
        for prodContainerId in prodContainersTCDAId:
            taxonomyResponse = self.copyProdContainerToGammaContainer(session, prodContainerId)
            if "SUCCESS" in taxonomyResponse:
                return prodContainerId, taxonomyResponse["SUCCESS"]
        if "ERROR" in taxonomyResponse:
            return prodContainerId, taxonomyResponse["ERROR"]
        return prodContainerId, "Unknown error occurred"

    def copyProdContainerToGammaContainer(self, session, prodContainerTCDAId):
        url = self.url + "copyContainer"
        data = json.dumps({"containerId": prodContainerTCDAId})
        if self.cookies == ApplicationsConstants.EMPTY_STRING:
            requestResponse = HttpRequest(session, url, data, ApplicationsMapConstants.TCDA_HEADERS).getRequestResponse("POST")
            self.cookies = dict(session.cookies.items())
        taxonomyResponse = HttpRequest(session, url, data, ApplicationsMapConstants.TCDA_HEADERS, self.cookies).getRequestResponse("POST")
        return taxonomyResponse