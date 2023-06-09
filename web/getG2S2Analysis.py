import sys
import getpass
import urllib3
import xlsxwriter
from utils import *
from temporaryUtils import *
from carrierData import CarrierData
from authentication import Authentication
import applicationsConstants as ApplicationsConstants
from shorttermutils import *

urllib3.disable_warnings()
sys.dont_write_bytecode = True

def makeworkbook(uniqueTemplates, templateG2S2Fields, templateShipmethodMap, CarrierG2S2Data, shipmethodG2S2Fields, newmasterFile):
    workbook = xlsxwriter.Workbook(newmasterFile)
    headerFormat = workbook.add_format({'bold': True, 'fg_color': '3DD4F5', 'align': 'center', 'valign': 'vcenter'})
    for index, template in enumerate(uniqueTemplates):
        if len(template) > 31:
            templateG2S2Sheet = workbook.add_worksheet(template[:31])
        else:
            templateG2S2Sheet = workbook.add_worksheet(template)
        templateG2S2Sheet.set_column('A:G', 25)
        templateG2S2Sheet.write(0, 0, "Template Name:")
        templateG2S2Sheet.write(0, 1, template)
        templateShipmethod = list(templateShipmethodMap[template])
        header = ["G2S2 field", "CarrierG2S2Data"]
        header.extend(templateShipmethod)
        templateG2S2Sheet.write_row(2, 0, header, headerFormat)
        for index_, g2s2field in enumerate(templateG2S2Fields[template]):
            templateG2S2Sheet.write(index_ + 3, 0, g2s2field)
            if g2s2field in CarrierG2S2Data:
                try:
                    templateG2S2Sheet.write(index_ + 3, 1, CarrierG2S2Data[g2s2field])
                except:
                    templateG2S2Sheet.write(index_ + 3, 1, '\n'.join([f'{key}: {value}' for key, value in CarrierG2S2Data[g2s2field].items()]))
            for _index_, shipmethod in enumerate(templateShipmethod):
                if g2s2field in shipmethodG2S2Fields[shipmethod]:
                    try:
                        templateG2S2Sheet.write(index_ + 3, _index_ + 2, shipmethodG2S2Fields[shipmethod][g2s2field])
                    except:
                        templateG2S2Sheet.write(index_ + 3, _index_ + 2, \
                            '\n'.join([f'{key}: {value}' for key, value in shipmethodG2S2Fields[shipmethod][g2s2field].items()]))
    workbook.close()

if __name__ == "__main__":
    printColoured(f"\nHello, you logged in as  {getpass.getuser()}", "green")
    printColoured(f"[INFO]: Authentication going on for user {getpass.getuser()} ...", "green")
    auth = Authentication(maxRedirects=15)
    auth.sentryAuthentication()
    printColoured("[INFO]: Sentry authentication done !!", "green")
    auth.midwayAuthentication()
    printColoured("[INFO]: Midway authentication done !!", "green")
    session = auth.session
    carrier, region, orgs = getCarrierRegionOrg()
    carrierData = CarrierData(carrier, region, orgs, False)
    printColoured("Fetching ship methods ...", "green")
    shipmethods = getShipmethodsFromExcel(session, carrierData)
    printColoured(f"[INFO]: Number of ship method available: {len(shipmethods)}", "green")
    if len(shipmethods) == 0:
        printColoured(f"[WARN]: Zero shipmethod found for carrier: {carrierData.carrier}", "yellow")
        sys.exit()
    shipmethodTemplates, shipmethodShippingLabels = getShipmethodTemplates(session, carrierData, shipmethods)
    uniqueTemplates = getUniqueTemplatesFromCarrierTemplates(shipmethodTemplates)
    templateShipmethod = getMappedShipmethodToTemplates(shipmethodTemplates, uniqueTemplates)
    templateG2S2Fields = getG2S2FieldsForTemplates(session, carrierData, uniqueTemplates, templateShipmethod, shipmethodShippingLabels)
    shipmethodG2S2Fields = getG2S2FieldsForShipmethods(session, carrierData, shipmethods)
    CarrierG2S2Data = getG2S2FieldsForCarrier(session, carrierData)
    newmasterFile = carrier + ApplicationsConstants.G2S2_ANALYSIS_FILE_EXTENSION
    makeworkbook(uniqueTemplates, templateG2S2Fields, templateShipmethod, CarrierG2S2Data, shipmethodG2S2Fields, newmasterFile)
    printColoured(f"\n[INFO]: Workbook with name {newmasterFile} has been created\n", "green")