import json
import requests
import utils
from exception import AuthError
from exception import MaxNumberOfRequest
from exception import BadRequest
import applicationsConstants as ApplicationsConstants

class HttpRequest(object):
    """
    Class use to get data by hitting get and post request to the given api with required
    data, headers and cookies.
    """

    def __init__(self, session, url, data={}, headers={}, cookies={}, maxRetries=ApplicationsConstants.MAX_RETRIES):
        """
        Constructor for Request.

        Parameters
        ----------
        session: session
            Session object to authenticate the request.
        url: str
            Url of the API.
        data: dict or json str(optional)
            Data accepts by the API.
            If not given default value used {}
        headers: dict(optional)
            Headers can be sent for the api.
            If not given default value used {}
        cookies: dict(optional)
            Cookies for the request.
            If not given default value used {}
        maxRetries: int(optional)
            Maximum number of times we should try to hit request if it fails.
            If not given set to ApplicationsConstants.MAX_RETRIES
        """
        self.session = session
        self.url = url
        self.data = data
        self.headers = headers
        self.cookies = cookies
        self.maxRetriesAllowed = maxRetries

    def getRequestResponse(self, requestType, requestAttemptNumber = 0):
        """
        Method use to get response from the API by putting request.

        Parameters
        ----------
        requestType: str
            Defines what type of request it is. Example: GET or POST.
        requestAttemptNumber: int(optional)
            Represents the number of times request has been already tried.
            If not given default value used 0.
        """
        if requestType == "GET":
            response = self.session.get(url = self.url, data = self.data, headers = self.headers, cookies = self.cookies)
        else:
            response = self.session.post(url = self.url, data = self.data, headers = self.headers, cookies = self.cookies)
        responseTextJson = utils.convert2json(response.text)
        if not response.ok and response.status_code == 401:
            raise AuthError("Unauthenticated request, You should authenticate (may use mwinit)")
        elif response.status_code == 404 and requestAttemptNumber < self.maxRetriesAllowed or \
                "ok" in responseTextJson and not responseTextJson["ok"] and requestAttemptNumber < self.maxRetriesAllowed:
            return self.getRequestResponse(requestType, requestAttemptNumber + 1)
        elif response.status_code == 400:
            raise BadRequest()
        elif requestAttemptNumber == self.maxRetriesAllowed:
            raise MaxNumberOfRequest()
        return responseTextJson
