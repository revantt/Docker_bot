from ast import ExceptHandler
import json
from utils import convert2json
from httpRequest import HttpRequest
from carrierData import CarrierData
import applicationsConstants as ApplicationsConstants
import applicationsMapConstants as ApplicationsMapConstants

class CitNewMaster():
    def __init__(self, carrierData):
        self.carrierData = carrierData
        self.url = self.getURL()
        self.cookies = ApplicationsConstants.EMPTY_STRING

    def getURL(self):
        return ApplicationsMapConstants.CIT_NEW_MASTER_URL[self.carrierData.region]

    def getLabelStream(self, session, anti_csrftoken_a2z, containerDetails):
        url = self.url + "getLabel"
        headers = { "anti-csrftoken-a2z":anti_csrftoken_a2z, "Content-Type": "application/json" }
        data = {"inputType":containerDetails["inputType"], "input":containerDetails["input"], \
             "stack":containerDetails["stack"], "labelFormat":containerDetails["labelFormat"]}
        if self.cookies == ApplicationsConstants.EMPTY_STRING:
            response = HttpRequest(session, url, json.dumps(data), headers).getRequestResponse("POST")
            self.cookies = dict(session.cookies.items())
        try:
            response = HttpRequest(session, url, json.dumps(data), headers, self.cookies).getRequestResponse("POST")
            if "images" in response:
                return response["images"][0]
        except:
            print("Exception occured")
        return ApplicationsConstants.EMPTY_STRING
