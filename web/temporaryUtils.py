import os
import re
import json
import base64
import requests
from shutil import rmtree
from atrops import Atrops
from kibanaDataAccessor import KibanaDataAccessor
from citNewMaster import CitNewMaster
from eagleEye import EagleEye
from utils import uploadFileInDrive
from monitorportalDataAccessor import MonitorPortalDataAccessor
from transLogisticsDataAccessor import TransLogisticsDataAccessor
from utils import printColoured
from utils import getFileDataFromPackage
from utils import getFileLocationFromPackage
import applicationsConstants as ApplicationsConstants
import applicationsMapConstants as ApplicationsMapConstants
from g2s2Accessor import G2S2Accessor
from taxonomy import Taxonomy
from utils import getBeautifyHTML

"""
# Method use to get user input for carrier, region and org list.
# @return (carrier, region, orgs): carrier, region, orgs entered by user.
"""
def getCarrierRegionOrg():
    print("Note: Org list should be space separated, To best use of the script all the configuration for carrier region and org should be correct")
    carrier = input("Please enter carrier Name: ")
    region = input("Please enter region: ")
    orgs = input("Please enter org list: ")
    return carrier, region, orgs

"""
# Method use to get shipmethods for a carrier from transLogistics.
# @param session: session object to authenticate the request.
# @param carrierData: object of carrierData which consists of the carrier related information.
# @return shipmethods: available shipmethod list for a given carrier from the transLogistics.
"""
def getShipmethods(session, carrierData):
    transLogisticsDataAccessor = TransLogisticsDataAccessor(carrierData)
    shipmethods = transLogisticsDataAccessor.getCarrierShipmethods(session)
    return shipmethods

"""
# Method use to get carriers for a region from transLogistics.
# @param session: session object to authenticate the request.
# @param carrierData: object of carrierData which consists basic information.
# @return carriersList: available carrier list for a given region from the transLogistics.
"""
def getCarriersList(session, carrierData):
    transLogisticsDataAccessor = TransLogisticsDataAccessor(carrierData)
    carriersList = transLogisticsDataAccessor.getRegionCarriers(session)
    return carriersList

"""
# Method use to get active and inactive status for shipmethod from the kibana.
# @param session: session object to authenticate the request.
# @param carrierData: object of carrierData which consists of the carrier related information.
# @param shipmethods: shipmethod list for which active and inactve status needs to find.
# @return kibanaShipmethodStatus: dictionary which consists of active and inactive status for every shipmethod using Kibana.
"""
def getActiveInactiveFromKibana(session, carrierData, shipmethods):
    kibanaShipmethodStatus = dict()
    kibanaDataAccessor = KibanaDataAccessor(carrierData)
    for shipmethod in shipmethods:
        print("Getting status from Kibana for shipmethod: ", shipmethod)
        shipmethodstatus = kibanaDataAccessor.getShipmethodActiveInactiveStatus(session, shipmethod, \
            ApplicationsConstants.KIBANA_TLGS_REQUEST_INDEX)
        kibanaShipmethodStatus[shipmethod] = "Inactive"
        if shipmethodstatus:
            kibanaShipmethodStatus[shipmethod] = "Active"
    return kibanaShipmethodStatus

"""
# Method use to get active and inactive status for shipmethod from the Atrops.
# @param session: session object to authenticate the request.
# @param carrierData: object of carrierData which consists the carrier related information.
# @param shipmethods: shipmethod list for which active and inactve status needs to find.
# @return atropsShipmethodStatus: dictionary which consists of active and inactive status for every shipmethod using Atrops.
"""
def getActiveInactiveFromAtrops(session, carrierData, shipmethods):
    atropsShipmethodStatus = dict()
    atrops = Atrops(carrierData)
    for shipmethod in shipmethods:
        print("Getting status from Atrops for shipmethod: ", shipmethod)
        shipmethodstatus = atrops.getShipmethodActiveInactiveStatus(session, shipmethod)
        atropsShipmethodStatus[shipmethod] = "Inactive"
        if shipmethodstatus:
            atropsShipmethodStatus[shipmethod] = "Active"
    return atropsShipmethodStatus

"""
# Method use to get active and inactive status for shipmethod from the Monitorportal.
# @param session: session object to authenticate the request.
# @param carrierData: object of carrierData which consists of the carrier related information.
# @param shipmethods: shipmethod list for which active and inactve status needs to find.
# @return monitorportalShipmethodStatus: dictionary which consists of active and inactive status for every shipmethod using Monitorportal.
"""
def getActiveInactiveFromMonitorportal(session, carrierData, shipmethods):
    monitorportalShipmethodStatus = dict()
    monitorPortalDataAccessor = MonitorPortalDataAccessor(carrierData)
    for shipmethod in shipmethods:
        print("Getting status from Monitorportal for shipmethod: ", shipmethod)
        shipmethodstatus =  monitorPortalDataAccessor.getShipmethodActiveInactiveStatus(session, shipmethod, ApplicationsConstants.TRANS_LABEL_GENERATION_SERVICE)
        monitorportalShipmethodStatus[shipmethod] = "Inactive"
        if shipmethodstatus:
            monitorportalShipmethodStatus[shipmethod] = "Active"
    return monitorportalShipmethodStatus

"""
# Method use to get N day call rate for shipmethod from monitorportal.
# @param session: session object to authenticate the request.
# @param carrierData: object of carrierData which consists of the carrier related information.
# @param shipmethods: shipmethod list for which active and inactve status needs to find.
# @return monitorportalShipmethodCallRate: call rate for every shipmethod from monitorportal.
"""
def getNDayCallRateFromMonitorportal(session, carrierData, shipmethods):
    monitorportalShipmethodCallRate = dict()
    monitorPortalDataAccessor = MonitorPortalDataAccessor(carrierData)
    for shipmethod in shipmethods:
        monitorportalShipmethodCallRate[shipmethod] = {"oneDay":0, "sevenDays":0, "thirtyDays":0, "sixtyDays":0}
        print("Getting call rate from Monitorportal for shipmethod: ", shipmethod)
        monitorportalShipmethodCallRate[shipmethod]["oneDay"] =  monitorPortalDataAccessor.getShipmethodVolumeFromMonitorportal(session, shipmethod, ApplicationsConstants.TRANS_LABEL_GENERATION_SERVICE, 1, False)
        monitorportalShipmethodCallRate[shipmethod]["sevenDays"] =  monitorPortalDataAccessor.getShipmethodVolumeFromMonitorportal(session, shipmethod, ApplicationsConstants.TRANS_LABEL_GENERATION_SERVICE, 7, False)
        monitorportalShipmethodCallRate[shipmethod]["thirtyDays"]  =  monitorPortalDataAccessor.getShipmethodVolumeFromMonitorportal(session, shipmethod, ApplicationsConstants.TRANS_LABEL_GENERATION_SERVICE, 30, False)
        monitorportalShipmethodCallRate[shipmethod]["sixtyDays"] =  monitorPortalDataAccessor.getShipmethodVolumeFromMonitorportal(session, shipmethod, ApplicationsConstants.TRANS_LABEL_GENERATION_SERVICE, 60, False)
    return monitorportalShipmethodCallRate

def getCarrierCallRateFromMonitorportal(session, carriersList):
    monitorportalCarrierCallRate = dict()
    for carrierdata in carriersList:
        carrierName = carrierdata.carrier
        monitorPortalDataAccessor = MonitorPortalDataAccessor(carrierdata)
        monitorportalCarrierCallRate[carrierName] = {"oneDay":0, "sevenDay":0}
        monitorportalCarrierCallRate[carrierName]["oneDay"] =  monitorPortalDataAccessor.getCarrierVolumeFromMonitorportal(session,carrierName , ApplicationsConstants.GET_LABEL_BY_ID, ApplicationsConstants.TRANS_LABEL_GENERATION_SERVICE, 1)
        monitorportalCarrierCallRate[carrierName]["sevenDay"] =  monitorPortalDataAccessor.getCarrierVolumeFromMonitorportal(session,carrierName , ApplicationsConstants.GET_LABEL_BY_ID, ApplicationsConstants.TRANS_LABEL_GENERATION_SERVICE, 7)
    return monitorportalCarrierCallRate

"""
# Method use to get templates for the shipmethod from G2S2.
# @param session: session object to authenticate the request.
# @param carrierData: object of carrierData which consists of the carrier related information.
# @param shipmethods: shipmethod list for which templates needs to find.
# @return shipmethodTemplates: templates mapped to each shipmethod.
"""
def getShipmethodTemplates(session, carrierData, shipmethods):
    shipmethodTemplates = dict()
    shipmethodShippingLabels = dict()
    g2s2Accessor = G2S2Accessor()
    for shipmethod in shipmethods:
        print("Getting template for shipmethod: ", shipmethod)
        shipmethodTemplatesAndShippingLabel = g2s2Accessor.getShipmethodTemplatesAndShippingLabels(session, \
            carrierData.region, shipmethod)
        shipmethodTemplates[shipmethod] = shipmethodTemplatesAndShippingLabel["templates"]
        shipmethodShippingLabels[shipmethod] = shipmethodTemplatesAndShippingLabel["shippingLabels"]
    return shipmethodTemplates, shipmethodShippingLabels

def getLabelStreams(session, carrierData, shipmethods):
    imageStreams = dict()
    containerId = dict()
    kibanaDataAccessor = KibanaDataAccessor(carrierData)
    citNewMaster = CitNewMaster(carrierData)
    eagleeye = EagleEye(carrierData)
    anti_csrftoken_a2z =  getCSRFtoken(session, ApplicationsMapConstants.CIT_NEW_MASTER_URL[carrierData.region] + "label-reprint", "anti-csrftoken-a2z")
    for shipmethod in shipmethods:
        imageStreams[shipmethod] = ApplicationsConstants.EMPTY_STRING
        containerId[shipmethod] = ApplicationsConstants.EMPTY_STRING
        container = kibanaDataAccessor.getNContainers(session, shipmethod, 1)
        if len(container) == 0:
            continue
        container = container[0]["_source"]
        if "tcdaContainerId" in container:
            details = eagleeye.getContainerDetailsUsingScanable(session, container["tcdaContainerId"])
            if "orderingShipmentId" in details:
                shipmentId = details["orderingShipmentId"]
                containerDetails = {"inputType": "SHIPMENT_ID", "input": shipmentId, "stack":container["Stack"], \
                    "labelFormat":container["labelFormat"]}
                containerId[shipmethod] = container["tcdaContainerId"]
                imageStreams[shipmethod] = citNewMaster.getLabelStream(session, anti_csrftoken_a2z, containerDetails).replace(' ', '+')
                print("Generated Label Stream for", shipmethod)
    return imageStreams, containerId

def getProdContainersTCDAId(session, carrierData, shipmethods):
    prodContainers = {}
    kibanaDataAccessor = KibanaDataAccessor(carrierData)
    for shipmethod in shipmethods:
        prodContainers[shipmethod] = list()
        containers = kibanaDataAccessor.getNContainers(session, shipmethod, 25)
        for container in containers:
            if "tcdaContainerId" in container["_source"]:
                prodContainers[shipmethod].append(container["_source"]["tcdaContainerId"])
        print(f"Getting prod container for shipmethod: {shipmethod}")
    return prodContainers

def generateGammaContainer(session, carrierData, prodContainersTCDAId):
    kibanaDataAccessor = KibanaDataAccessor(carrierData)
    eagleeye = EagleEye(carrierData)
    taxonomy = Taxonomy(carrierData)
    containers = {}
    for shipmethod in prodContainersTCDAId:
        containers[shipmethod] = {"prodContainer":"", "gammaContainer":""}
        if prodContainersTCDAId[shipmethod] != list():
            print(f"Generating gamma container for shipmethod: {shipmethod}")
            containers[shipmethod]["prodContainer"], containers[shipmethod]["gammaContainer"] = \
                taxonomy.generateGammaContainer(session, prodContainersTCDAId[shipmethod])
    return containers

def uploadImagesOnDrive(driveDirName, imageStreams):
    if not os.path.exists(driveDirName):
        os.makedirs(driveDirName)
    for key, value in imageStreams.items():
        imageName = key
        imageStream = value
        imageName = os.path.join(driveDirName, imageName + ".jpg")
        if imageStream != "":
            imgdata = base64.b64decode(imageStream)
            with open(imageName, 'wb') as f:
                f.write(imgdata)
            uploadFileInDrive(imageName, driveDirName)
            print("Uploaded image for Shipmethod: ", imageName)
    if os.path.exists(driveDirName):
        rmtree(driveDirName)

"""
# Method use to get rateCardsInformation for the shipmethod from translogistics.
# @param session: session object to authenticate the request.
# @param carrierData: object of carrierData which consists of the carrier related information.
# @param shipmethods: shipmethod list for which rateCardsInformation needs to find.
# @return rateCardInformation: rateCardInformation for all of the given shipmethods.
# @return shipmethodRatecard: Ratecard names for all of the given shipmethods.
"""
def getShipmethodsRateCardsInformation(session, carrierData, shipmethods):
    allRateCardsName = set()
    rateCardInformation = dict()
    shipmethodRatecard = dict()
    transLogisticsDataAccessor = TransLogisticsDataAccessor(carrierData)
    for shipmethod in shipmethods:
        print("Getting rate card names for Shipmethod: ", shipmethod)
        rateCardsName = transLogisticsDataAccessor.getShipmethodRateCardNames(session, shipmethod)
        allRateCardsName.update(rateCardsName)
        shipmethodRatecard[shipmethod] = rateCardsName

    for rateCardName in allRateCardsName:
        print("Getting RateCards Information: ", rateCardName)
        rateCardInformation[rateCardName]  = transLogisticsDataAccessor.getRateCardInformation(session, rateCardName)

    return rateCardInformation, shipmethodRatecard

"""
# Method use to get shipmethodRestrictions for the shipmethod from translogistics.
# @param session: session object to authenticate the request.
# @param carrierData: object of carrierData which consists of the carrier related information.
# @param shipmethods: shipmethod list for which shipmethodRestrictions needs to find.
# @return shipmethodRestrictions: shipmethodRestrictions for all of the given shipmethods.
"""
def getShipmethodRestrictions(session, carrierData, shipmethods):
    transLogisticsDataAccessor = TransLogisticsDataAccessor(carrierData)
    shipmethodRestrictions = dict()
    for shipmethod in shipmethods:
        print("Getting Shipmethod Restrictions: ", shipmethod)
        shipmethodRestriction = transLogisticsDataAccessor.getShipmethodRestrictions(session, shipmethod)
        shipmethodRestrictions[shipmethod] = shipmethodRestriction
    return shipmethodRestrictions

"""
# Method use to parse shipmethod RateCard Information.
# @param rateCardsName: ratecard names list.
# @param rateCardInformation: rateCardInformation for all of the given shipmethods.
# @return shipmethodAtropsRate: shipmethodAtropsRate for the given rateCardsName.
"""
def parseShipmethodRateCardInformation(rateCardsName, rateCardInformation):
    shipmethodAtropsRate = ""
    for rateCardName in rateCardsName:
        shipmethodAtropsRate += ApplicationsConstants.NEW_LINE + rateCardInformation[rateCardName]["rateType"] + ": "
        rateCardDetail = rateCardInformation[rateCardName]["rateCardDetail"]
        currencyUnit = rateCardInformation[rateCardName]["currencyUnit"]
        if type(rateCardDetail) == str:
            shipmethodAtropsRate += str(rateCardDetail)
        else:
            if "rateCardDetailMinMax" in rateCardDetail:
                shipmethodAtropsRate += str(rateCardDetail["rateCardDetailMinMax"]) + currencyUnit
            else:
                shipmethodAtropsRate += str(rateCardDetail["rateCardDetailMin"]) + " " + currencyUnit +" - " +  str(rateCardDetail["rateCardDetailMax"]) + " " + currencyUnit
    return shipmethodAtropsRate.strip()

"""
# Method use to parse shipmethod restriction Information.
# @param shipmethodRestrictions: shipmethodRestrictions for shipmethod.
# @return weight: weight for the given shipmethod.
# @return dimension: dimension for the given shipmethod.
# @return packageValue: packageValue for the given shipmethod.
# @return otherRestrictions: otherRestrictions for the given shipmethod.
"""
def parseShipethodRestriction(shipmethodRestrictions):
    weight, dimension, packageValue = ("", "", "")
    otherRestrictions = list()
    if "SCALE_WEIGHT" in shipmethodRestrictions:
        weight =  ApplicationsConstants.DOUBLE_NEW_LINE.join(shipmethodRestrictions["SCALE_WEIGHT"])
        del shipmethodRestrictions["SCALE_WEIGHT"]
    if "DIMENSIONS" in shipmethodRestrictions:
        dimension =  ApplicationsConstants.DOUBLE_NEW_LINE.join(shipmethodRestrictions["DIMENSIONS"])
        del shipmethodRestrictions["DIMENSIONS"]
    if "PACKAGE_VALUE" in shipmethodRestrictions:
        packageValue =  ApplicationsConstants.DOUBLE_NEW_LINE.join(shipmethodRestrictions["PACKAGE_VALUE"])
        del shipmethodRestrictions["PACKAGE_VALUE"]
    for restrictionType in shipmethodRestrictions:
        otherRestrictions.append(ApplicationsConstants.DOUBLE_NEW_LINE.join(shipmethodRestrictions[restrictionType]))
    otherRestrictions = ApplicationsConstants.DOUBLE_NEW_LINE.join(otherRestrictions)
    return weight, dimension, packageValue, otherRestrictions

"""
# Method use to get the data for SMDeconstruction from ATROPS and transLogistics.
# @param session: session object to authenticate the request.
# @param carrierData: object of carrierData which consists of the carrier related information.
# @param shipmethods: shipmethod list for which templates needs to find.
# @return smDeconstructionData: smDeconstructionData for every shipmethods.
"""
def getSMDeconstructionData(session, carrierData, shipmethods):
    smDeconstructionData = {}
    atrops = Atrops(carrierData)
    transLogisticsDataAccessor = TransLogisticsDataAccessor(carrierData)
    g2s2ShipMethodAccessor = G2S2Accessor()
    rateCardInformation, shipmethodRatecard = getShipmethodsRateCardsInformation(session, carrierData, shipmethods)
    shipmethodRestrictions = getShipmethodRestrictions(session, carrierData, shipmethods)
    for shipmethod in shipmethods:
        smDeconstructionData[shipmethod] = dict()
        print("Getting Shipmethod Templates: ", shipmethod)
        shipmethodTemplatesAndShippingLabel = g2s2ShipMethodAccessor.getShipmethodTemplatesAndShippingLabels(session, carrierData.region, shipmethod)
        templates = shipmethodTemplatesAndShippingLabel["templates"]
        shipmethodShippingLabels = shipmethodTemplatesAndShippingLabel["shippingLabels"]
        zplTemplates = ApplicationsConstants.NEW_LINE.join(templates["ZPL"]) if "ZPL" in templates else \
            ApplicationsConstants.EMPTY_STRING
        pngTemplates = ApplicationsConstants.NEW_LINE.join(templates["PNG"]) if "PNG" in templates else \
            ApplicationsConstants.EMPTY_STRING
        templates = zplTemplates + ApplicationsConstants.NEW_LINE + pngTemplates
        weight, dimension, packageValue, otherRestrictions = parseShipethodRestriction(shipmethodRestrictions[shipmethod])
        smDeconstructionData[shipmethod]["ShipMethod Name"] = shipmethod;
        smDeconstructionData[shipmethod]["Region"] = carrierData.region;
        smDeconstructionData[shipmethod]["Label Templates"] = templates
        smDeconstructionData[shipmethod]["Atrops Link"] = atrops.getAtropsDataLink(shipmethod)
        smDeconstructionData[shipmethod]["Weight"] = weight
        smDeconstructionData[shipmethod]["Dimensions"] = dimension
        smDeconstructionData[shipmethod]["Package Value"] = packageValue
        smDeconstructionData[shipmethod]["Other restrictions"] = otherRestrictions
        smDeconstructionData[shipmethod]["Atrops rate"] = parseShipmethodRateCardInformation(shipmethodRatecard[shipmethod], \
            rateCardInformation)
    return smDeconstructionData

def pickTemplate(carrierData, templateLocation, shippingLabel):
    shippingLabelsToken = shippingLabel.split("_")
    pickedTemplate = list()
    if shippingLabelsToken[0] == "HQ":
        pickedTemplate = [location for location in templateLocation if "/" + shippingLabelsToken[1] + "/" in location]
    elif shippingLabelsToken[0] == "AFN":
        pickedTemplate = [location for location in templateLocation if "/" + shippingLabelsToken[1] + "/" in location]
    else:
        pickedTemplate = [location for location in templateLocation if "/" + carrierData.region + "/" in location]
    return pickedTemplate

def getG2S2FieldsOfTemplate(session, carrierData, template, templateShippingLabels):
    g2s2Fields = list()
    templateLocation = getFileLocationFromPackage(session, ApplicationsConstants.LABEL_TEMPLATES_PACKAGE_NAME, "production", template);
    if len(templateLocation) == 0:
        printColoured("[ERROR]: NO templates found with template name " + template + " in the package " + ApplicationsConstants.LABEL_TEMPLATES_PACKAGE_NAME, "red")
        return g2s2Fields
    pickedTemplate = templateLocation[0]
    if len(templateLocation) != 1:
        printColoured("[Warn]: Multiple templates found with template name " + template + " in the package " + ApplicationsConstants.LABEL_TEMPLATES_PACKAGE_NAME, "yellow")
        printColoured("Multiple Templates are: " + str(templateLocation), "yellow")
        if len(templateShippingLabels) != 1:
            printColoured("[WARN]: Multiple shipping label found for template name " + template + " in the package " + ApplicationsConstants.LABEL_TEMPLATES_PACKAGE_NAME, "red")
            printColoured("[INFO]: Multiple shipping labels are "+ str(templateShippingLabels), "yellow")
            templateShippingLabels.sort()
            for shippingLabel in templateShippingLabels:
                pickedTemplate = pickTemplate(carrierData, templateLocation, shippingLabel)
                if len(pickedTemplate) != 0:
                    break
        else:
            pickedTemplate = pickTemplate(carrierData, templateLocation, templateShippingLabels[0])
        if len(pickedTemplate) != 0:
            pickedTemplate = pickedTemplate[0]
        printColoured("[Info]: Taking template "+ pickedTemplate + " because selected region is " + carrierData.region, "green")
    templateData = getFileDataFromPackage(session, ApplicationsConstants.LABEL_TEMPLATES_PACKAGE_NAME, "production", pickedTemplate)
    templateData = templateData.replace(ApplicationsConstants.NEW_LINE, ApplicationsConstants.SPACE)
    g2s2Fields = re.findall("(?<=\$!g2s2Data\.)\w+", templateData)
    return list(set(g2s2Fields))

def getG2S2FieldsForShipmethods(session, carrierData, shipmethods):
    shipmethodG2S2Fields = dict()
    g2s2Accessor = G2S2Accessor()
    for shipmethod in shipmethods:
        print("Getting g2s2 fields for shipmethod: ", shipmethod)
        g2s2Fields = g2s2Accessor.getShipmethodG2S2Data(session, shipmethod, carrierData.orgs)
        shipmethodG2S2Fields[shipmethod] = g2s2Fields
    return shipmethodG2S2Fields

def getG2S2FieldsForCarrier(session, carrierData):
    print("Getting g2s2 fields for carrier: ", carrierData.carrier)
    g2s2Accessor = G2S2Accessor()
    return g2s2Accessor.getCarrierG2S2Data(session, carrierData.carrier, carrierData.orgs)

def getUniqueTemplatesFromCarrierTemplates(shipmethodTemplates):
    uniqueTemplates = set()
    for shipmethod, template in shipmethodTemplates.items():
        if "ZPL" in template:
            uniqueTemplates.update(list(template["ZPL"]))
        if "PNG" in template:
            uniqueTemplates.update(list(template["PNG"]))
    return uniqueTemplates

def getG2S2FieldsForTemplates(session, carrierData, templates, templateShipmethod, shipmethodShippingLabels):
    templateG2S2Fields = dict()
    for template in templates:
        templateShippingLabels = set()
        for shipmethod in templateShipmethod[template]:
            templateShippingLabels.update(shipmethodShippingLabels[shipmethod])
        templateG2S2Fields[template] = getG2S2FieldsOfTemplate(session, carrierData, template,  list(templateShippingLabels))
    return templateG2S2Fields

def getMappedShipmethodToTemplates(shipmethodTemplates, uniqueTemplates):
    templateShipmethod = {}
    for template in uniqueTemplates:
        templateShipmethod[template] = set()
        for shipmethod, shipmethodTemplate in shipmethodTemplates.items():
            if "ZPL" in shipmethodTemplate and template in shipmethodTemplate["ZPL"] or \
                    "PNG" in shipmethodTemplate and template in shipmethodTemplate["PNG"]:
                templateShipmethod[template].add(shipmethod)
    return templateShipmethod

def getShipmethodProposals(session, carrierData, shipmethods, configElement, uniqueProposalId=True):
    shipmethodProposalsCount = dict()
    atrops = Atrops(carrierData)
    for shipmethod in shipmethods:
        print(f"Getting proposal count for shipmethod: {shipmethod}")
        shipmethodProposalsCount[shipmethod] = atrops.getShipmethodProposalCount(session, shipmethod, configElement, uniqueProposalId)
    return shipmethodProposalsCount

def getShipmethodStatus(shipmethodCallRate):
    activeInactiveStatus = {}
    for shipmethod in shipmethodCallRate:
        shipmethodData = shipmethodCallRate[shipmethod]
        shipmethodDataCallRate = shipmethodData["oneDay"] + shipmethodData["sevenDays"] +  \
            shipmethodData["thirtyDays"] + shipmethodData["sixtyDays"]
        if shipmethodDataCallRate > 0:
            activeInactiveStatus[shipmethod] = "Active"
        else:
            activeInactiveStatus[shipmethod] = "Inctive"
    return activeInactiveStatus

def getCSRFtoken(session, url, tokenName):
    response = session.get(url, verify=False)
    soup = getBeautifyHTML(response.text)
    csrfToken = soup.find('input',attrs = {'name':tokenName})['value']
    return csrfToken