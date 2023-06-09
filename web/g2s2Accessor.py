import re
import hjson
from utils import convert2json
from exception import BadRequest
from httpRequest import HttpRequest
from utils import mergeDictsIntoDict
import applicationsConstants as ApplicationsConstants
import applicationsMapConstants as ApplicationsMapConstants

class G2S2Accessor():
    """ Class use to get the data from G2S2 """

    def getShippingLabelList(self, regionCode):
        """
        Method use to get the shipping label list for given regionCode.

        Parameters
        ----------
        regionCode: str
            Represents region for which shipping label list needs to find.

        Returns
        -------
        shippingLabelList: list
            Shipping labels for region defined in carrierData.
        """
        shippingLabelList = ApplicationsMapConstants.SHIPPING_LABEL[regionCode]
        for org in ApplicationsMapConstants.ORGS[regionCode]:
            shippingLabelList.append(f"_{org}_SHIPPING_LABEL");
        return shippingLabelList

    def getG2S2TableData(self, session, tableName, g2s2SearchKeyValue, stage_version):
        """
        Method use to get the data from g2s2 table.

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        tableName: str
            Name of the g2s2 table from which data needs to fetch.
        g2s2SearchKeyValue: dict
            Key value pair using which we can search data in given table.
        stage_version: str
            Stage version need to use for this table in g2s2.

        Returns
        -------
        g2s2Response: json
            Data from the given g2s2 table in the form of json.
        """
        url = ApplicationsConstants.G2S2_BASE_URL + f"g2s2?url=metadata/{tableName}/?stage_version=@{stage_version}"
        for key, value in g2s2SearchKeyValue.items():
            url = f"{url}%26{key}={value}"
            print("URL ___  ",url)
        try:
            g2s2Response = HttpRequest(session, url).getRequestResponse("GET")
        except BadRequest:
            g2s2Response = HttpRequest(session, url, cookies=dict(session.cookies.items())).getRequestResponse("GET")
        return g2s2Response

    def getShipmethodTemplatesAndShippingLabels(self, session, regionCode, shipmethod):
        """
        Method use to get the mapped templates and shipping labels for particular shipmethod.

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        regionCode: str
            regionCode used to find shipping label list to fliter the templates.
        shipmethod: str
            Shipmethod for which mapped templates and shipping labels needs to find.

        Returns
        -------
        shipmethodTemplatesAndShippingLabel: dict
            Mapped templates and shipping labels for given shipmethod.
        """
        shippingLabelList = self.getShippingLabelList(regionCode)
        shipmethodTemplatesAndShippingLabel = {"templates":{}, "shippingLabels":set()}
        g2s2SearchKeyValue = {"template_ship_method": shipmethod}
        g2s2Response = self.getG2S2TableData(session, "cit_labeling_service_template_mapping", g2s2SearchKeyValue, \
            "labeling_serviceProd")
        for template in g2s2Response["payload"]:
            shippingLabel = template["template_override_hierarchy"]
            templateContentType = template["template_content_type"]
            if shippingLabel in shippingLabelList:
                templateNameRegex = re.compile('.*template_name:\\"([^#]+?)".*')
                citLabelingServiceTemplateMapping = template["ionPayload"].replace(ApplicationsConstants.NEW_LINE, \
                    ApplicationsConstants.SPACE).strip()
                matcher = templateNameRegex.match(citLabelingServiceTemplateMapping)
                templateName = matcher.group(1)
                if templateContentType not in shipmethodTemplatesAndShippingLabel["templates"]:
                    shipmethodTemplatesAndShippingLabel["templates"][templateContentType] = set([templateName])
                else:
                    shipmethodTemplatesAndShippingLabel["templates"][templateContentType].add(templateName)
                shipmethodTemplatesAndShippingLabel["shippingLabels"].add(shippingLabel)
        return shipmethodTemplatesAndShippingLabel

    def getShipmethodG2S2Data(self, session, shipmethod, orgList):
        """
        Method use to get the g2s2 related data for particular shipmethod from gts_ship_method_data g2s2 table.
        If shipmethod contains multiple org and each org contains different data it will provide that data
        as g2s2field: {<org1>: data1, <org2>: data2, <org3>: data3} otherwise <g2s2field>: <data>

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        shipmethod: str
            Shipmethod for which g2s2 data needs to find.
        orgList: list
            Org list required to filter out the shipmethod data on the basis of org.

        Returns
        -------
        g2s2ShipmethodData: dict
            Shipmethod data in the form of dict.
        """
        shipmethodDetails = list()
        g2s2SearchKeyValue = {"template_ship_method": shipmethod}
        g2s2Response = self.getG2S2TableData(session, "gts_ship_method_data", g2s2SearchKeyValue, "labeling_service_data_Prod")
        if int(g2s2Response["totalResultSize"]) == 0:
            return shipmethodDetails
        for shipmethodData in g2s2Response["payload"]:
            if shipmethodData["gts_org"] in orgList:
                if "gts_ship_method_data::" in shipmethodData["ionPayload"]:
                    shipmethodData = dict(hjson.loads(shipmethodData["ionPayload"] \
                        .replace("gts_ship_method_data::", "").replace(",\n", '\n')))
                elif "ship_method_data::" in shipmethodData["ionPayload"]:
                    shipmethodData = dict(hjson.loads(shipmethodData["ionPayload"] \
                        .replace("ship_method_data::", "").replace(",\n", '\n')))
                shipmethodDetails.append(shipmethodData)
        g2s2ShipmethodData = mergeDictsIntoDict(shipmethodDetails, "gts_org")
        return g2s2ShipmethodData

    def getCarrierG2S2Data(self, session, carrierName, orgList):
        """
        Method use to get the carrier data from gts_carrier_data g2s2 table.
        If carrier contains multiple org and each org contains different data it will provide that
        data as g2s2field: {<org1>: data1, <org2>: data2, <org3>: data3} otherwise <g2s2field>: <data>

        Parameters
        ----------
        session: requests.session
            Session object to authenticate the request.
        carrierName: str
            Carrier name for which g2s2 data required.
        orgList: list
            Org list required to filter out the carrier data on the basis of org.

        Returns
        -------
        g2s2CarrierData: dict
            Carrier data in the form of dict.
        """
        g2s2SearchKeyValue = {"gts_carrier": carrierName}
        g2s2Response = self.getG2S2TableData(session, "gts_carrier_data", g2s2SearchKeyValue, "labeling_service_data_Prod")
        if int(g2s2Response["totalResultSize"]) == 0:
            return dict()
        g2s2CarrierDetails = []
        for carrierData in g2s2Response["payload"]:
            if carrierData["gts_org"] in orgList:
                carrierData = dict(hjson.loads(carrierData["ionPayload"].replace("gts_carrier_data::", "").replace(",\n", '\n')))
                g2s2CarrierDetails.append(carrierData)
        g2s2CarrierData = mergeDictsIntoDict(g2s2CarrierDetails, "gts_org")
        return g2s2CarrierData

'''
    Not included template_override_hierarchy
    'CN',      ['JOYO_CD_STD_D2D', 'SFEXP_OVERSEA_STD', 'DHL_OVERSEA_STD', 'FEDEX_EXP_OVERSEA', 'UPS_EXP_OVERSEA']
    'AFN_INSC_SHIPPING_LABEL': ['ATS_SELLER', 'ATS_INJ_GRD_STD', etc]
    'AFN_WARMUP', [SERVICE_WARMUP_LABEL]
    'AFN_GLOBAL_SUPPLEMENTARY' [FROZEN]
    'AFN_WARMUP_SHIPPING_LABEL', [SERVICE_WARMUP_LABEL]
    'AFN_GLOBAL_CLP_HAZMAT_LABEL', [CLP_HAZMAT_LABEL]
    'HQ_WARMUP_SHIPPING_LABEL': ['VFO_WARMUP_LABEL', 'SERVICE_WARMUP_LABEL', 'ZPL_WARMUP_LABEL']
    'FR': [AMZN_IT_STD]
'''
