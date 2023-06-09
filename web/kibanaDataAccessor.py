import time
import json
from httpRequest import HttpRequest
import applicationsConstants as ApplicationsConstants
import applicationsMapConstants as ApplicationsMapConstants

class KibanaDataAccessor():
    """ Class use to get the data from kibana """

    def __init__(self, carrierData):
        """
        Constructor for KibanaDataAccessor.

        Parameters
        ----------
        carrierData: carrierData
            CarrierData object which have all of the basic information about the carrier.
        """
        self.carrierData = carrierData
        self.kibanaBaseURL = self.getKibanaBaseURL(carrierData.region)
        self.cookies = None

    def getKibanaBaseURL(self, regionCode):
        """
        Method use to get the base url of kibana for given regionCode.

        Parameters
        ----------
        regionCode: str
            Region for which kibana base url needs to find.

        Returns
        -------
        kibanaBaseUrl: str
            Kibana base url for given region code.

        Raises
        ------
        ValueError
            If kibana is not yet setup for given regionCode.
        """
        if regionCode in ApplicationsMapConstants.KIBANA_NOT_SUPPORTED_REGIONS:
            raise ValueError(f"Kibana for {regionCode} region is not yet setup")
        return ApplicationsMapConstants.KIBANA_URL[regionCode]

    def getKibanaMustRequestResponse(self, session, url, index, query, size, days, excludeFields):
        """
        Method use to get the response from kibana using required fields.

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        url: str
            Kibana url uniform resource locator where request needs to hit.
        index: str
            Kibana index for which request needs to make.
        query: str
            User query for which request needs to hit.
        size: int
            Indicates for how many number of hits data should be present in response.
        days: int
            Number of days for which request needs to make.
        excludeFields: str
            Fields which needs to excludes from kibana response.

        Returns
        -------
        requestResponse: json
            Json response from the kibana.
        """
        data = self.getDataForKibanaMustRequest(index, query, size, days, excludeFields)
        if self.cookies == None:
            requestResponse = HttpRequest(session, url, data, ApplicationsMapConstants.KIBANA_HEADERS).getRequestResponse("POST")
            self.cookies = dict(session.cookies.items())
        requestResponse = HttpRequest(session, url, data, ApplicationsMapConstants.KIBANA_HEADERS, self.cookies).getRequestResponse("POST")
        return requestResponse

    def getShipmethodActiveInactiveStatus(self, session, shipmethod, index):
        """
        Method use to get the active and inactive status for a given shipmethod from kibana.
        If kibana have any single hit in the last sixty days for the shipmethod it will return True.

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        shipmethod: str
            Shipmethod for which active and inactive status needs to find.
        index: str
            Kibana index for which request needs to make.

        Returns
        -------
        boolean
            Active and inactive status for the shipmethod.
            True represents active and False represents inactive.
        """
        numberOfHits = self.getShipmethodVolumeFromKibana(session, shipmethod, index, 60)
        return numberOfHits > 0

    def getShipmethodVolumeFromKibana(self, session, shipmethod, index, days):
        """
        Method use to get the volume for a given shipmethod from Kibana within given number of days.
        This method calculates the day from instant time. The time at which the request made.

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        shipmethod: str
            Shipmethod for which volume needs to find.
        index: str
            Kibana index for which shipmethod volume needs to find.
        days: int
            Number of days for which shipmethod volume needs to find.

        Returns
        -------
        numberOfHits: int
            Number of hits within given number of days.
        """
        url = self.kibanaBaseURL + "elasticsearch/_msearch?rest_total_hits_as_int=true&ignore_throttled=true"
        kibanaResponse = self.getKibanaMustRequestResponse(session, url, index, shipmethod.upper(), 0, days, "*")
        numberOfHits = kibanaResponse["responses"][0]["hits"]["total"]
        return numberOfHits

    def getDataForKibanaMustRequest(self, index, query, size, days, excludeFields):
        """
        Method use to get data for kibana request.

        Parameters
        ----------
        index: str
            Kibana index for which request needs to make.
        query: str
            User query for which request needs to hit.
        size: int
            Indicates for how many number of hits data should be present in response.
        days: int
            Number of days for which request needs to make.
        excludeFields: str
            Fields which needs to excludes from kibana response.

        Returns
        -------
        data: ndjson type str
            Data string in ndjson form.
        """
        currentTimeInMilliSeconds = int(round(time.time() * 1000))
        data = [
                {"index":index, "ignore_unavailable":True},
                {
                    "version": True,
                    "size": size,
                    "_source": {
                        "excludes": [excludeFields]
                    },
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "query_string": {
                                        "query": query,
                                        "analyze_wildcard": True,
                                        "default_field": "*"
                                    }
                                },
                                {
                                    "range": {
                                        "@timestamp": {
                                        "gte": int(currentTimeInMilliSeconds - \
                                            ApplicationsConstants.MILISECONDS_IN_DAY * days),
                                        "lte": int(currentTimeInMilliSeconds),
                                        "format": "epoch_millis"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            ]
        data = ApplicationsConstants.NEW_LINE.join(json.dumps(d) for d in data) + ApplicationsConstants.NEW_LINE
        return data

    def getNContainers(self, session, shipmethod, size):
        url = self.kibanaBaseURL + "elasticsearch/_msearch?rest_total_hits_as_int=true&ignore_throttled=true"
        index = ApplicationsConstants.KIBANA_TLGS_REQUEST_INDEX
        gte = int(round(time.time() * 1000)) - ApplicationsConstants.MILISECONDS_IN_DAY * 1825
        lte = int(round(time.time() * 1000))
        kibanaResponse = self.getKibanaMustRequestResponse(session, url, index, shipmethod.upper(), size = size, \
            days = 60, excludeFields = "")
        if "responses" in kibanaResponse and kibanaResponse["responses"][0]["hits"]["total"] > 0:
            return kibanaResponse["responses"][0]["hits"]["hits"]
        return dict()
