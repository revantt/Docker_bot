import json
import numpy as np
import pandas as pd
from utils import convert2json
from utils import printColoured
from httpRequest import HttpRequest
from exception import MaxNumberOfRequest
import applicationsMapConstants as ApplicationsMapConstants

class TransLogisticsDataAccessor():
    """ Class use to get the data from Trans-Logistics """

    def __init__(self, carrierData):
        """
        Constructor for TransLogisticsDataAccessor.

        Parameters
        ----------
        carrierData: carrierData
            CarrierData object which have all the basic information about the carrier.
        """
        self.carrierData = carrierData
        self.urlPrefix = ApplicationsMapConstants.TRANS_LOGISTICS_URL[self.carrierData.region]

    def getCarrierShipmethods(self, session, useGlobalRegion=False):
        """
        Method use to get the shipmethods for the carrier.

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        useGlobalRegion: boolean(optional)
            Set it as TRUE if shipmethods needs to find for the carrier globally.
            If not given default value used False.

        Returns
        -------
        list
            Available shipmethod list for given carrier from the transLogistics.
        """
        shipmethodList = list()
        url = self.urlPrefix + "getSearchParamsAjax"
        countryList = self.carrierData.orgs
        carrierName = self.carrierData.carrier
        useEnabledSM = self.carrierData.useEnabledSM
        data = {"entity":"shipMethod", "countryList":countryList, "carrierList":carrierName, "isGlobalRegion": useGlobalRegion, \
            "enabledSMFlag": useEnabledSM}
        try:
            requestResponse = HttpRequest(session, url, data).getRequestResponse("POST")
            if requestResponse["ok"]:
                shipmethodList = requestResponse["data"]
        except MaxNumberOfRequest:
            printColoured(f"[ERROR] We are not able to get response from {url} " \
                f"while retrieving shipmethods for carrier {self.carrierData.carrier} " \
                f"and region {self.carrierData.region} please try again later!!", "red")
        return shipmethodList

    def getRegionCarriers(self, session, useGlobalRegion=False):
        """
        Method use to get the carriers available in regions.

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        useGlobalRegion: boolean(optional)
            Set it as TRUE if carrier needs to find globally.
            If not given default value used False.

        Returns
        -------
        list
            Available carrier list for given region from the transLogistics.
        """
        carrierList = list()
        url = self.urlPrefix + "getSearchParamsAjax"
        countryList = self.carrierData.orgs
        data = {"entity":"carrier", "countryList":countryList, "isGlobalRegion": useGlobalRegion}
        try:
            requestResponse = HttpRequest(session, url, data).getRequestResponse("POST")
            if requestResponse["ok"]:
                carrierList = requestResponse["data"]
        except MaxNumberOfRequest:
            printColoured(f"[ERROR] We are not able to get response from {url} " \
                f"while retrieving carriers for region {self.carrierData.region} " \
                f"please try again later!!", "red")
        return carrierList

    """
    # Method use to get the rate cards for the shipmethod from the transLogistics.
    # @param session:  session object to authenticate the request.
    # @param shipmethod: shipmethod for which rate card names need to find.
    # @return rateCardNames: available rate cards names for given shipmethod.
    """
    def getShipmethodRateCardNames(self, session, shipMethod):
        rateCardNames = list()
        url = self.urlPrefix + "getSearchParamsAjax"
        data = {"entity":"rateCardNames", "shipMethodList": shipMethod}
        requestResponse = HttpRequest(session, url, data).getRequestResponse("POST")
        while not requestResponse["ok"]:
            if "errorMessage" in requestResponse:
                printColoured("[WARN]: Error occurred while retriving rate card names for shipmethod " + shipMethod + " : "  + requestResponse["errorMessage"], "yellow")
            elif "message" in requestResponse:
                printColoured("[WARN]: Error occurred while retriving rate card names for shipmethod " + shipMethod + " : "  + requestResponse["message"], "yellow")
            requestResponse = HttpRequest(session, url, data).getRequestResponse("POST")
        rateCardNames = requestResponse["data"]
        return rateCardNames

    """
    # Method use to get the rate card type and its conditions for the ratecard.
    # @param session: session object to authenticate the request.
    # @param rateCardName: rateCardName for which rate card type and conditions needs to find.
    # @return rateType and conditions : rate card type and its conditions for the given ratecard.
    """
    def getRateCardConditionsType(self, session, rateCardName):
        url = self.urlPrefix + "readSMConfigAjax"
        data = {"entity": "rates-new", "rateCardNames": rateCardName, "unmappedOnly": "false"}
        requestResponse = HttpRequest(session, url, data).getRequestResponse("POST")
        while not requestResponse["ok"]:
            if "errorMessage" in requestResponse:
                printColoured("[WARN]: In while loop " + requestResponse["errorMessage"], "yellow")
            elif "message" in requestResponse:
                printColoured("[WARN]: In while loop " + requestResponse["message"], "yellow")
            requestResponse = HttpRequest(session, url, data).getRequestResponse("POST")
        return requestResponse["aaData"][0]["rateType"], requestResponse["aaData"][0]["conditions"]

    """
    # Method use to get the rate card information for the shipmethod from the transLogistics.
    # @param session: session object to authenticate the request.
    # @param rateCardInformation: all available rateCardInformation for other rate card.
    # @param rateCardsNames: rateCardsNames for which rateCardInformation needs to find.
    # @return rateCardInformation: rateCardInformation after updating with given rateCardsNames.
    """
    def getRateCardInformation(self, session, rateCardName):
        rateCardInformation = dict()
        url = self.urlPrefix + "readSMConfigAjax"
        rateType, rateCardConditions = self.getRateCardConditionsType(session, rateCardName)
        rateCardInformation = {"rateType": rateType, "conditions": rateCardConditions}
        data = {"entity": "rate-card-details", "rateCardName": rateCardName, "conditionNames": rateCardConditions}
        requestResponse = HttpRequest(session, url, data).getRequestResponse("POST")
        while not requestResponse["ok"]:
            printColoured("[WARN]: In while loop for rate card: " + rateCardName, "yellow")
            requestResponse = HttpRequest(session, url, data).getRequestResponse("POST")
        aaData = requestResponse["aaData"][0]
        rateCardInformation["currencyUnit"] = aaData["currencyMeasurementUnit"]["unit"]
        if aaData["rateCardLevelValue"] != None:
            rateCardInformation["rateCardDetail"] = aaData["rateCardLevelValue"]
        elif aaData["ratesValueMap"] != None:
            if len(aaData["ratesValueMap"]) == 1 and aaData["ratesValueMap"][0][1] == "Step":
                minMaxRateCard = self.getMinMaxRate([[rate.split()[0] for rate in aaData["ratesValueMap"][0]]])
            else:
                if aaData["ratesValueMap"][-1][1] == "Step":
                    aaData["ratesValueMap"].pop()
                minMaxRateCard = self.getMinMaxRate(aaData["ratesValueMap"])
            rateCardInformation["rateCardDetail"] = minMaxRateCard
        return rateCardInformation

    """
    # Method use to get min and max rate from rateCard Detail.
    # @para rateCardDetail: rateCardDetails for which minimum and maximum rate card needs to find.
    # @return dict: minimum and maximum value from given ratecardDetail.
    """
    def getMinMaxRate(self, rateCardDetail):
        rateCardDetail = np.array(rateCardDetail)
        rateCardDetail[rateCardDetail==None] = np.nan
        rateCardDetail = np.delete(rateCardDetail, [0,1,2], 1)
        rateCardDetail = pd.to_numeric(rateCardDetail.flatten(), errors='coerce')
        min_ = np.nanmin(rateCardDetail)
        max_ = np.nanmax(rateCardDetail)
        if min_ == max_:
            return {"rateCardDetailMinMax":max_}
        return {"rateCardDetailMin":min_, "rateCardDetailMax":max_}

    """
    # Method use to get the restriction around shipmethod from the transLogistics.
    # @param session: session object to authenticate the request.
    # @param shipmethod: shipmethod for which restrictions need to find.
    # @return shipmethodRestrictions: restrictions for the given shipmethod.
    """
    def getShipmethodRestrictions(self, session, shipmethod, restrictionType=None):
        shipmethodRestrictions = {}
        url = self.urlPrefix + "readSMConfigAjax"
        if restrictionType != None:
            data = {"restrictionType":restrictionType, "entity":"carrier-restrictions", "carrierList": self.carrierData.carrier, "shipMethodList": shipmethod}
        else:
            data = {"entity":"carrier-restrictions", "carrierList": self.carrierData.carrier, "shipMethodList": shipmethod}
        requestResponse = HttpRequest(session, url, data).getRequestResponse("POST")
        while not requestResponse["ok"]:
            if "errorMessage" in requestResponse:
                printColoured("[WARN]: error occured while retrieving restriction for shipmethod " + shipmethod + " : " + requestResponse["errorMessage"], "yellow")
            elif "message" in requestResponse:
                printColoured("[WARN]: error occured while retrieving restriction for shipmethod " + shipmethod + " : " + requestResponse["message"], "yellow")
            requestResponse = HttpRequest(session, url, data).getRequestResponse("POST")
        for restriction in requestResponse["aaData"]:
            if restriction["expression"] == None:
                continue
            try:
                shipmethodRestrictions[restriction["restrictionType"]].append(restriction["expression"])
            except:
                shipmethodRestrictions[restriction["restrictionType"]] = [restriction["expression"]]
        return shipmethodRestrictions
