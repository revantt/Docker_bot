from ast import excepthandler
from carrierData import CarrierData
from httpRequest import HttpRequest
from utils import getBeautifyHTML
import applicationsConstants as ApplicationsConstants
from utils import printColoured

""" class use to get data from Atrops """
class Atrops():
    def __init__(self, carrierData):
        self.carrierData = carrierData
        self.url = self.getURL()

    """ Method use to get the base url of Atrops """
    def getURL(self):
        return ApplicationsConstants.ATROPS_BASE_URL

    """
    # Method use to get the atrops data link for any shipmethod.
    # @param shipmethod: shipmethod for which atrops data link needs to find.
    # @return url: atrops url from where we can get the atrops data for the shipmethod.
    """
    def getAtropsDataLink(self, shipmethod):
        url = self.url + "shipmethod?database=staging_prod&shipmethod="+ shipmethod
        return url

    """
    # Method use to get the active and inactive status for shipmethod from the atrops.
    # If Atrops have any single enabled warehouseId it will mark it as True.
    # @param session: session object to authenticate the request.
    # @param shipmethod: shipmethod for which active and inactive status need to find.
    # @return boolean: True means Active and False means Inactive.
    """
    def getShipmethodActiveInactiveStatus(self, session, shipmethod):
        htmlData = self.getShipmethodWarehouseData(session, shipmethod)
        if htmlData:
            return htmlData.find("tr", "enabled") != None
        return False

    """
    # Method use to get the FCID for the shipmethod from the atrops.
    # @param session: session object to authenticate the request.
    # @param shipmethod: shipmethod for which FCID needs to find.
    # @param warehouseEnabledDisabled: FCID for enabled warehouseId or disabled warehousId
    # @return boolean: True means Active and False means Inactive.
    """
    def getShipmethodWareHouseIds(self, session, shipmethod, warehouseEnabledDisabled):
        htmlData = self.getShipmethodWarehouseData(session, shipmethod)
        if htmlData:
            allRows = htmlData.find_all("tr", warehouseEnabledDisabled)
            FCList = list()
            for row in allRows:
                rowData = row.find_all("td", "center")
                country = rowData[0].text
                if country in self.carrierData.orgs:
                    FCList.append(rowData[1].text)
            return FCList
        return []
    
    """
    # Method use to get the WarehouseData for the shipmethod from the atrops.
    # @param session: session object to authenticate the request.
    # @param shipmethod: shipmethod for which warehouse data needs to find.
    # @return htmlData: warehouse data for given shipmethod.
    """
    def getShipmethodWarehouseData(self, session, shipmethod):
        url = self.url + "get_warehouses_by_shipmethod?database=staging_prod&shipmethod=" + shipmethod.upper()
        print("calling for shipmethod: "+ shipmethod)
        requestResponse = None
        try:
            requestResponse = HttpRequest(session, url).getRequestResponse("GET")
        except:
            print("Not found")
        if requestResponse:
            htmlData = getBeautifyHTML(requestResponse["data"])
            return htmlData
        return requestResponse
        

    def getAtropsCCSProposalSearchURL(self, shipmethod, configElement, start, size, dateSortType):
        return f"http://search-atrops-ccs-proposal-search2-bzav4exeb2drjbb6iqb22le5yq.us-east-1.cloudsearch.amazonaws.com/2013-01-01/search?return=proposalid,deploymentdate_ymd&q=" \
            f"{shipmethod}%20{configElement}%20%0D%0A&start={start}&size={size}&sort=deploymentdate_ymd {dateSortType}"

    def getProposals(self, session, shipmethod, configElement, dateSortType):
        url = self.getAtropsCCSProposalSearchURL(shipmethod, configElement, 0, 10000, dateSortType)
        return HttpRequest(session, url).getRequestResponse("GET")

    def getUniqueProposals(self, session, shipmethod, configElement):
        proposalIds = set()
        proposals = self.getProposals(session, shipmethod, configElement, "desc")
        for proposal in proposals["hits"]["hit"]:
            proposalIds.add(proposal["fields"]["proposalid"])
        if proposals["hits"]["found"] > 10000:
            printColoured(f"[WARN] ATROPS can return maximum 10000 records but for shipmethod {shipmethod} " \
                f"total {proposals['hits']['found']} record found there might be discrepancy "\
                    f"in data for shipmethod {shipmethod}", "yellow")
            proposals = self.getProposals(session, shipmethod, configElement, "asc")
            for proposal in proposals["hits"]["hit"]:
                proposalIds.add(proposal["fields"]["proposalid"])
        return len(proposalIds)

    def getShipmethodProposalCount(self, session, shipmethod, configElement, uniqueProposalId):
        if uniqueProposalId:
            return self.getUniqueProposals(session, shipmethod, configElement)
        return self.getProposals(session, shipmethod, configElement, "desc")["hits"]["found"]