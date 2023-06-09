import sys
import time
import getpass
import urllib3
import xlsxwriter
from temporaryUtils import *
from utils import printColoured
from carrierData import CarrierData
from utils import getPrintableTable
from authentication import Authentication
import applicationsConstants as ApplicationsConstants
from shorttermutils import *

# To disable unverified HTTPS request is being made to host.
urllib3.disable_warnings()

# To not generate the bytecode i.e. .pyc files.
sys.dont_write_bytecode = True

def makeworkbook(filename, templates):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    headerFormat = workbook.add_format({'bold': True, 'fg_color': '3DD4F5', 'align': 'center', 'valign': 'vcenter'})
    secondheaderFormat = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
    worksheet.set_column('A:C', 50)
    worksheet.merge_range(0, 1, 0, 2, 'Merged Range')
    templatemappingHeader = ["ShipMethod", "Template Name"]
    templatemappingHeader1 = ["", "ZPL", "PNG"]
    worksheet.write_row(0, 0, templatemappingHeader, headerFormat)
    worksheet.write_row(1, 0, templatemappingHeader1, secondheaderFormat)
    row = 2
    for shipmethod in templates:
        zpltemplates = ApplicationsConstants.NEW_LINE.join(templates[shipmethod]["ZPL"]) if "ZPL" in templates[shipmethod] else "-"
        pngtemplates = ApplicationsConstants.NEW_LINE.join(templates[shipmethod]["PNG"]) if "PNG" in templates[shipmethod] else  "-"
        worksheet.write(row, 0,  shipmethod)
        worksheet.write(row, 1,  zpltemplates)
        worksheet.write(row, 2,  pngtemplates)
        row += 1
    workbook.close()

def preprocessdata(templates):
    data = list()
    for template in templates:
        data_ = [template]
        data_.append(ApplicationsConstants.NEW_LINE.join(templates[template]["ZPL"])) if "ZPL" in templates[template] else data_.append("-")
        data_.append(ApplicationsConstants.NEW_LINE.join(templates[template]["PNG"])) if "PNG" in templates[template] else data_.append("-")
        data.append(data_)
    return data

def printTable(templates):
    data = preprocessdata(templates)
    headers = ['Shipmethod', 'ZPL', 'PNG']
    table = getPrintableTable(data, headers)
    print(table)

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
    templates, shipmethodShippingLabels = getShipmethodTemplates(session, carrierData, shipmethods)
    filename = "shipmethodTemplates_" + str(int(time.time())) +".xlsx"
    if len(shipmethods) > 0:
        makeworkbook(filename, templates)
    printTable(templates)
    printColoured(f"\n[INFO]: Workbook with name {filename} has been created\n", "green")
