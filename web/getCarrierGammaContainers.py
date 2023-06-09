import sys
import time
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

def makeworkbookWithLabelImages(filename, containers):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("Containers")
    headerFormat = workbook.add_format({'bold': True, 'fg_color': '3DD4F5', 'align': 'center', 'valign': 'vcenter'})
    worksheet.set_column('A:C', 40)
    worksheet.set_column('D:D', 80)
    textFormat = workbook.add_format({'text_wrap': True})
    templatemappingHeader = ["ShipMethod", "Prod TCDA Container", "Prod Gamma Container", "Prod Label Image"]
    worksheet.write_row(0, 0, templatemappingHeader, headerFormat)
    row = 1
    for shipmethod in containers:
        worksheet.write(row, 0,  shipmethod, textFormat)
        worksheet.write(row, 1,  containers[shipmethod]["prodContainer"], textFormat)
        worksheet.write(row, 2,  containers[shipmethod]["gammaContainer"], textFormat)
        row += 1
    workbook.close()

if __name__ == "__main__":
    username = getpass.getuser()
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
    prodContainersTCDAId = getProdContainersTCDAId(session, carrierData, shipmethods)
    containers = generateGammaContainer(session, carrierData, prodContainersTCDAId)
    filename = carrierData.carrier + "_gammaContainers_" + str(int(time.time())) +".xlsx"
    makeworkbookWithLabelImages(filename, containers)
    print("\nWorkbook with name", filename, "has been created\n")
