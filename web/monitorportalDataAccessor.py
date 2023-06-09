import yaml
import pandas
from io import StringIO
from httpRequest import HttpRequest
import applicationsConstants as ApplicationsConstants
import applicationsMapConstants as ApplicationsMapConstants

class MonitorPortalDataAccessor():
    """ Class use to get the data from MonitorPortal """

    def __init__(self, carrierData):
        """
        Constructor for MonitorPortalDataAccessor.

        Parameters
        ----------
        carrierData: carrierData
            CarrierData object which have all of the basic information about the carrier.
        """
        self.marketplaceList = ApplicationsMapConstants.MARKETPLACE[carrierData.region]
        self.monitorPortalBaseURL = ApplicationsConstants.MONITORPORTAL_BASE_URL

    def getShipmethodActiveInactiveStatus(self, session, shipmethod, serviceName):
        """
        Method use to get the active and inactive status for a given shipmethod from monitorportal.
        If monitorportal shows any single call in the last thirty days for the shipmethod it will return True.

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        shipmethod: str
            Shipmethod for which active and inactive status needs to find.
        serviceName: str
            Service name for which request needs to make.

        Returns
        -------
        boolean
            Active and inactive status for the shipmethod.
            True represents active and False represents inactive.
        """
        numberOfHits = self.getShipmethodVolumeFromMonitorportal(session, shipmethod, serviceName, 30, True)
        return numberOfHits > 0

    def getShipmethodVolumeFromMonitorportal(self, session, shipmethod, servicename, days, acitveInactive):
        """
        Method use to get the volume for a given shipmethod from monitorportal within given number of days.

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        shipmethod: str
            Shipmethod for which volume needs to find.
        serviceName: str
            Service name for which request needs to make.
        days: int
            Number of days for which shipmethod volume needs to find.
        acitveInactive: bool
            Use to check if volume required to get active and inactive status for shipmethod.

        Returns
        -------
        numberOfHits: int
            Number of hits within given number of days.
        """
        numberOfHits = 0
        metricNames = self.getMetricNames(session, shipmethod, servicename)
        if len(metricNames) == 0:
            return numberOfHits
        for marketplace in self.marketplaceList:
            url = self.getMonitorportalMWSURL(marketplace, servicename, metricNames, days)
            requestResponse = HttpRequest(session, url).getRequestResponse("GET")
            dataFrame = pandas.read_csv(StringIO(requestResponse["data"]), sep=",")
            dataFrame.drop(dataFrame.head(5).index, inplace=True)
            dataFrame.drop(dataFrame.columns[[0]], axis=1, inplace=True)
            dataFrame.fillna(0, inplace=True)
            numberOfHits += dataFrame.astype("float64").values.sum()
            if acitveInactive and numberOfHits > 0:
                return numberOfHits
        return numberOfHits

    def getMetricNames(self, session, shipmethod, servicename):
        """
        Method use to get active metric names for a given shipmethod which ends with GetLabelById_Start.

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        shipmethod: str
            Shipmethod for which metric names need to find.
        serviceName: str
            Service name for which request need to hit.

        Returns
        -------
        metricsNames: list
            Active metric names for given shipmethod for given service name.
        """
        metricsNames = list()
        for marketplace in self.marketplaceList:
            url = self.monitorPortalBaseURL + f'search?search={shipmethod.upper()}%20dataset%3D%24Prod%24%20marketplace%3D%24' \
                f'{marketplace}%24%20servicename%3D%24{servicename}%24%20Start%20client%3D%24ALL%24%20schemaname%3DService%20' \
                    f'methodname%3D%24ALL'
            requestResponse = HttpRequest(session, url).getRequestResponse("GET")
            # monitorPortalMetricsResult = yaml.safe_load(requestResponse)
            monitorPortalMetricsResult = requestResponse
            if monitorPortalMetricsResult["results_available"] > 0:
                metrics = monitorPortalMetricsResult["metrics"]
                for metric in metrics:
                    metricname = metric["metricSchema"]["data"][9]
                    if metricname.startswith('TLGS:') and metricname.endswith(f":{shipmethod}:_:GetLabelById_Start"):
                        metricsNames.append(metricname)
                    if metricname.startswith('TLGS:') and metricname.endswith(f":{shipmethod}:_:GetLabelByIdOld_Start"):
                        metricsNames.append(metricname)
        return metricsNames

    def getMonitorportalMWSURL(self, marketplace, serviceName, metricNames, days):
        """
        Method use to get mws GetGraph URL of the monitoportal for the given serviceName and metricNames.

        Parameters
        ----------
        marketplace: str
            Marketplace used to fetch data from monitorportal.
        serviceName: str
            Service name for which request need to hit.
        metricsNames: list
            Active metric names for particular shipmethod for given service name.
        days: int
            Number of days for which shipmethod volume needs to find.

        Returns
        -------
        MWSGetGraphURL: str
            MWS GetGraph URL to fetch data from monitoportal.
        """
        if days <= 5:
            period = "OneMinute"
        else:
            period = "FiveMinute"
        url = ApplicationsConstants.MONITORPORTAL_GET_GRAPH_DATA_BASE_URL
        for index, metricName in enumerate(metricNames):
            url += f'&SchemaName{index+1}=Service&Metric{index+1}={metricName}'
        url += f"&Period={period}&ServiceName={serviceName}&Marketplace={marketplace}&StartTime1=-P{days}D&EndTime1=-PT0H" \
            "&OutputFormat=CSV_TRANSPOSE"
        return url

    def getCarrierVolumeFromMonitorportal(self, session, carrierName, serviceId, serviceName, days):
        numberOfHits = 0
        if days <= 5:
            period = "OneMinute"
        else:
            period = "FiveMinute"
        url = f'https://monitorportal.amazon.com/mws?Action=GetGraph&Version=2007-07-07&SchemaName1=Search&Pattern1={carrierName}%20{serviceId}' \
            f'%20dataset%3D%24Prod%24%20marketplace%3D%24{self.marketplaceList[0]}%24%20servicename%3D%24{serviceName}%24%20schemaname%3DService%20methodname%3D%24ALL%24%20Start&Period1={period}&' \
            f'Stat1=n&&&DecoratePoints=true&TZ=IST@TZ%3A%20IST&StartTime1=-P{days}D&EndTime1=-PT0H&FunctionExpression1=SUM%28S1%29&FunctionLabel1=Total%20%28sum%20of%20sums%3A%20%7Bsum%7D%29&FunctionYAxisPreference1=left&actionSource=iGraph&WidthInPixels=540&HeightInPixels=196&NoRedirect=1&forceRefresh=1621856476655&OutputFormat=CSV_TRANSPOSE'
        requestResponse = HttpRequest(session, url).getRequestResponse("GET")
        dataFrame = pandas.read_csv(StringIO(requestResponse["data"]), sep=",")
        dataFrame.drop(dataFrame.head(5).index, inplace=True)
        dataFrame.drop(dataFrame.columns[[0]], axis=1, inplace=True)
        dataFrame.fillna(0, inplace=True)
        numberOfHits += dataFrame.astype("float64").values.sum()
        return numberOfHits
