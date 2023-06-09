import os
import re
import requests
import urllib3
import traceback
from utils import convert2json
from exception import AuthError
import applicationsConstants as ApplicationsConstants
import applicationsMapConstants as ApplicationsMapConstants

class Authentication(object):
    """ Class use to get the session object to authenticate the user """

    def __init__(self, allowRedirects = False, maxRedirects = 8):
        """
        Constructor for authentication.

        Parameters
        ----------
        allowRedirects: boolean(optional)
            Set to True if POST/PUT/DELETE redirect following is allowed.
            If not given default value used False.
        maxRedirects: int(optional)
            Number of maximum redirects allowed.
            If not given default value used is 8.
        """
        self.session = requests.Session()
        self.session.max_redirects = maxRedirects
        self.session.allow_redirects = allowRedirects
        self.session.verify = False
        self.cookieFile = os.path.expanduser("~") + '/.midway/cookie'

    def sentryAuthentication(self):
        """
        Method use to do sentry authentication.

        Raises
        ------
        NewConnectionError
            If failed to establish a new connection.
        ConnectionError
            If failed to establish a connection.
        AuthError
            If sentry response is not ok.
        Exception
            If error encountered while getting sentry response.
        """
        try:
            response = self.session.post(ApplicationsConstants.SENTRY_BASE_URL)
        except urllib3.exceptions.NewConnectionError as exc:
            raise Exception("Failed to establish a new connection:") from exc
        except requests.exceptions.ConnectionError as exc:
            raise Exception(ApplicationsConstants.CONNECTION_ERROR_MESSAGE) from exc
        except Exception as e:
            traceback.print_exc()
        if not response.ok:
            raise AuthError(f"Sentry authentication failed due to response code {response.status_code}" \
                "There was some problem to authenticate you. please try again!!")

    def requestFollowRedirects(self, url, headers, data, maxHops=10):
        """
        Method use to follow every redirect request while doing midway authentication.

        Parameters
        ----------
        url: str
            Redirect uniform resource locator.
        headers: dict
            Authentication headers use to authenticate the request.
        data: dict
            Data needs to validate the request.
        maxHops: int(optional)
            Use to limit Number of redirects Followed.
            If not given set to 10.

        Returns
        -------
        json type str
            Response from the request.
        """
        if maxHops < 0:
            return False
        maxHops -= 1
        response = self.session.post(url, data=data, headers=headers , allow_redirects=False)
        if response.status_code == 302 or response.status_code == 307:
            return self.requestFollowRedirects(response.headers['Location'], headers, data)
        return response

    def midwayAuthentication(self):
        """
        Method use to do midway authentication.

        Raises
        ------
        AuthError
            If midway response is not ok and response status_code is 401 and midway response message is Unauthenticated
            or response status_code is 403.
        """
        cookieFile = open(self.cookieFile)
        for line in cookieFile:
            cookieTokens = re.sub(r'^#HttpOnly_', '', line.rstrip()).split()
            if len(cookieTokens) == 7:
                cookieObj = requests.cookies.create_cookie(domain=cookieTokens[0], name=cookieTokens[5], value=cookieTokens[6])
                self.session.cookies.set_cookie(cookieObj)
        midwayResponse = self.requestFollowRedirects(ApplicationsConstants.ISENGARD_SERVICE_BASE_URL, ApplicationsMapConstants.AUTHENTICATION_HEADERS, {})
        midwayResponseJson = convert2json(midwayResponse.text)
        if not midwayResponse.ok and midwayResponse.status_code == 401 and midwayResponseJson["message"] == "Unauthenticated":
            raise AuthError("Midway authentication fail", midwayResponseJson["desc"])
        elif midwayResponse.status_code == 403:
            raise AuthError(ApplicationsConstants.FORBIDDEN_ERROR_MESSAGE)
        cookieFile.close()
