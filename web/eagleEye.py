from utils import convert2json, printColoured
from httpRequest import HttpRequest
from carrierData import CarrierData
import applicationsConstants as ApplicationsConstants
import applicationsMapConstants as ApplicationsMapConstants
import time

class EagleEye(CarrierData):
    def __init__(self, carrierData):
        self.carrierData = carrierData
        self.url = self.getURL()

    def getURL(self):
        return ApplicationsMapConstants.EAGLE_EYE_URL[self.carrierData.region]

    def getEagleEyeResponseScanable(self, session, scanableId):
        url = self.getURL() + "scanable/" + scanableId
        response = HttpRequest(session, url).getRequestResponse("GET")
        if type(response) == list and len(response) > 0:
            return response[0]["package"]
        if response["ok"] and "data" in response and \
            response["data"] == "Too many input items received in short interval, please try again later. ( Allowed 50 id(s) in 60 sec(s). )":
            printColoured("Eagle eye allow 50 id(s) in 60 sec(s). Let's wait for 30 seconds to restart the eagle-eye request", "yellow")
            time.sleep(30)
            return self.getEagleEyeResponse(session, scanableId)
        return dict()

    def getEagleEyeResponseShipment(self, session, shipmentID):
        url = self.getURL() + "shipment/" + shipmentID
        response = HttpRequest(session, url).getRequestResponse("GET")
        if type(response) == list and len(response) > 0:
            return response[0]["package"]
        if response["ok"] and "data" in response and \
            response["data"] == "Too many input items received in short interval, please try again later. ( Allowed 50 id(s) in 60 sec(s). )":
            printColoured("Eagle eye allow 50 id(s) in 60 sec(s). Let's wait for 30 seconds to restart the eagle-eye request", "yellow")
            time.sleep(30)
            return self.getEagleEyeResponse(session, shipmentID)
        return dict()
    def getContainerDetailsUsingScanable(self, session, scanableId):
        url = self.getURL() + "scanable/" + scanableId
        response = HttpRequest(session, url).getRequestResponse("GET")
        if len(response) > 0:
            return response[0]["package"]
        return dict()

    def getDeliveryStatus(self, eagleEyeResponse):
        try:
            return eagleEyeResponse["details"][-1]["leg"]["compStatus"]
        except:
            return None

    def getTrackingId(self, eagleEyeResponse):
        try:
            return eagleEyeResponse["trackingId"]
        except:
            return None

    def getOrderId(self, eagleEyeResponse):
        try:
            return eagleEyeResponse["orderingOrderId"]
        except:
            return None

    def getShipmethod(self,eagleEyeResponse):
        try:
            return eagleEyeResponse["enrichedLegInfo"].split(' ')[0]
        except:
            return None

    def getShipmentId(self, eagleEyeResponse):
        try:
            return eagleEyeResponse["orderingShipmentId"]
        except:
            return None

    def getTCDAContainerId(self, eagleEyeResponse):
        try:
            return eagleEyeResponse["tcdaId"]
        except:
            return None

    def getEsmmInfo(self, eagleEyeResponse):
        try:
            return eagleEyeResponse["enrichedLegInfo"]
        except:
            return None