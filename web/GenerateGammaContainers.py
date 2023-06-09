import json
from httpRequest import HttpRequest
import applicationsConstants as ApplicationsConstants
import applicationsMapConstants as ApplicationsMapConstants


class GammaContainerGenerator:
    """ class to generate the TCDA gamma containers corresponding to prod containers list provided as input """

    def __init__(self, region, session):
        """
                Constructor for GenerateGammaContainers.

                Parameters
                ----------
                region: str
                    Region to which the set of I/P prodContainerIds belong.
        """
        self.region = region
        self.session = session
        self.cookies = ApplicationsConstants.EMPTY_STRING
        self.url = ApplicationsMapConstants.TAXONOMY_URL[region]

    def generateProdToGammaTCDAContainersMapping(self, prod_containers_id_list):

        """
        input prodContainerList
        returns a dictionary
        prodContainerId:gammaContainerId
        or
        prodContainerId:Error (if not able to get a corresponding gamma container)

        """
        prod_to_gamma_containers_map = {}
        request_response = ApplicationsConstants.EMPTY_STRING
        for prod_container_id in prod_containers_id_list:
            request_response = self.copyProdContainerToGammaContainer(prod_container_id)
            if "SUCCESS" in request_response:
                prod_to_gamma_containers_map[prod_container_id] = request_response["SUCCESS"]

            # Fallback to fetch gammaContainerId from ClientContainerId if copyContainerAPI return Error in response

            elif "ERROR" in request_response:
                error = request_response["ERROR"]
                pos = error.find("Error Code =") + len("Error Code =")
                attr = error[pos:].split(" ")[1]
                print("Error occurred while copying : " + prod_container_id + " " + attr)
                data = json.dumps({"containerId": prod_container_id})
                load_container_url = self.url + "loadContainer?containerId=" + prod_container_id + "&versionNumber="
                load_container_request_response = HttpRequest(self.session, load_container_url, data,
                                                              ApplicationsMapConstants.TCDA_HEADERS).getRequestResponse(
                    "GET")
                response_data = load_container_request_response['data']
                client_container_id = self.fetchClientContainerId(response_data)
                print(
                    "Trying to fetch corresponding gamma container using associated client container id :" + client_container_id)
                gamma_client_container_id_url = ApplicationsMapConstants.TAXONOMY_GAMMA_URL[
                                                    self.region] + "visualizeTCDAData?select_feature=Load&indexName=ClientContainerId&indexValue=" + client_container_id + "&versionNumber="
                cookies = dict(self.session.cookies.items())
                try:
                    taxonomy_response = HttpRequest(self.session, gamma_client_container_id_url, data,
                                                    ApplicationsMapConstants.TCDA_HEADERS, cookies).getRequestResponse(
                        "GET")
                    gamma_container_id = self.fetchGammaContainerId(taxonomy_response['data'])
                    print("Successfully fetched the gamma container with associated client container id ")
                    prod_to_gamma_containers_map[prod_container_id] = gamma_container_id
                except Exception as e:
                    prod_to_gamma_containers_map[prod_container_id] = "Error"
                    print("Error in getting the gamma container for " + prod_container_id + " " + str(e))
        return prod_to_gamma_containers_map

    def copyProdContainerToGammaContainer(self, prod_container_id):

        """
        input prodContainerId
        returns response returned from calling copyContainer API of TCDA Taxonomy :
        {"SUCCESS":"gammaContainerId"}
        {"ERROR":"Error Code = '', internalErrorCode = ' ', storageCode =  '', isRecoverable =  '' , Error Message =  "}

        """
        url = self.url + "copyContainer"
        data = json.dumps({"containerId": prod_container_id})
        if self.cookies == ApplicationsConstants.EMPTY_STRING:
            request_response = HttpRequest(self.session, url, data,
                                           ApplicationsMapConstants.TCDA_HEADERS).getRequestResponse(
                "POST")
        return request_response

    def fetchClientContainerId(self, data):
        """"
        input loadContainerRequestResponse['data']
        returns clientContainerId

        """
        container_data = data.split("\n")
        step = 0
        client_container_id = ""
        for i in range(len(container_data)):
            if "clientContainerId" in container_data[i]:
                step = 1
            elif step == 1 and "cellContent" in container_data[i]:
                step = 2
            elif step == 2:
                if len(container_data[i].strip()) != 0:
                    client_container_id = container_data[i].strip()
                    return client_container_id
        return client_container_id

    def fetchGammaContainerId(self, data):
        """
        input taxonomyResponse['data'] on loading gamma container for clientContainerId
        returns GammaContainerId
        """

        pos = data.index("containerId=") + 12
        return data[pos: pos + 29]
