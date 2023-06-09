import sys
import time
import getpass
import urllib3
import xlsxwriter
from shorttermutils import getShipmethodsFromExcel
from temporaryUtils import *
from utils import printColoured
from utils import getPrintableTable
from carrierData import CarrierData
from authentication import Authentication

# To disable unverified HTTPS request is being made to host.
urllib3.disable_warnings()

# To not generate the bytecode i.e. .pyc files.
sys.dont_write_bytecode = True

""" Make workbook with given data """
def makeworkbook(filename, smDeconstructionData):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("SMDeconstruction")
    headerFormat = workbook.add_format({'bold': True, 'fg_color': '3DD4F5', 'align': 'center', 'valign': 'vcenter'})
    secondheaderFormat = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
    worksheet.set_column('A:R', 15)
    smDeconstructionHeader = ["ShipMethod Name", "Region", "Service indicator", "Label Templates", "Weight",
    "Dimensions", "Package Value", "Other restrictions", "Atrops rate", "Atrops transit time", "Additional Information", "Queries"
    "Carrier Provided Service", "Value Added Services", "Why was it created as a seperate SM", "Was it due to some limitation in MLTS?", "comments"]
    worksheet.write_row(0, 0, smDeconstructionHeader, headerFormat)
    row = 2
    for shipmethod in smDeconstructionData:
        shipmethodSMDeconstructionData = smDeconstructionData[shipmethod]
        for col in range(0, 9):
            if col in [2]:
                continue
            worksheet.write(row, col,  shipmethodSMDeconstructionData[smDeconstructionHeader[col]])
            if col == 0:
                worksheet.write_url(row, col,  shipmethodSMDeconstructionData["Atrops Link"], string = shipmethod)
        row += 1
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
    smDeconstructionData = getSMDeconstructionData(session, carrierData, shipmethods)
    filename = "SMDeconstruction_" + carrierData.carrier +".xlsx"
    makeworkbook(filename, smDeconstructionData)
    printColoured(f"\n[INFO]: Workbook with name {filename} has been created\n", "green")