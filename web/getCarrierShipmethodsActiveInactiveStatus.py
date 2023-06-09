import sys
import time
import getpass
import urllib3
import xlsxwriter
from temporaryUtils import *
from utils import printColoured
from utils import getPrintableTable
from carrierData import CarrierData
from authentication import Authentication
from shorttermutils import *

""" To disable unverified HTTPS request is being made to host. """
urllib3.disable_warnings()

""" To not generate the bytecode i.e. .pyc files. """
sys.dont_write_bytecode = True

""" Make workbook with given data """
def makeworkbook(filename, shipmethods, atropsShipmethodStatus, monitorportalShipmethodStatus, monitorportalShipmethodCallRate):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("ActiveInactive")
    headerFormat = workbook.add_format({'bold': True, 'fg_color': '3DD4F5', 'align': 'center', 'valign': 'vcenter'})
    secondheaderFormat = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
    worksheet.set_column('A:H', 20)
    worksheet.merge_range(0, 1, 0, 3, 'Merged columns')
    worksheet.merge_range(0, 4, 0, 7, 'Call rates')
    activeInactiveHeader = ["ShipMethod", "Active / Inactive", "Call Rates"]
    activeInactiveHeader1 = ["", "Kibana", "Atrops", "Monitor", "1 Day", "7 Days", "30 Days", "60 Days"]
    worksheet.write_row(0, 0, activeInactiveHeader, headerFormat)
    worksheet.write_row(0, 4, ["Call Rates"], headerFormat)
    worksheet.write_row(1, 0, activeInactiveHeader1, secondheaderFormat)
    row = 2
    for shipmethod in shipmethods:
        worksheet.write(row, 0,  shipmethod)
        worksheet.write(row, 1,  "-")
        worksheet.write(row, 2,  atropsShipmethodStatus[shipmethod])
        worksheet.write(row, 3,  monitorportalShipmethodStatus[shipmethod])
        worksheet.write(row, 4,  monitorportalShipmethodCallRate[shipmethod]["oneDay"])
        worksheet.write(row, 5,  monitorportalShipmethodCallRate[shipmethod]["sevenDays"])
        worksheet.write(row, 6,  monitorportalShipmethodCallRate[shipmethod]["thirtyDays"])
        worksheet.write(row, 7,  monitorportalShipmethodCallRate[shipmethod]["sixtyDays"])
        row += 1
    workbook.close()

""" Preprocess the data to get printed in table format """
def preprocessdata(shipmethods, atropsShipmethodStatus, monitorportalShipmethodStatus, monitorportalShipmethodCallRate):
    data = list()
    for shipmethod in shipmethods:
        data.append([shipmethod, atropsShipmethodStatus[shipmethod], monitorportalShipmethodStatus[shipmethod], \
            monitorportalShipmethodCallRate[shipmethod]])
    return data

""" To print the data in the table format """
def printTable(shipmethods, atropsShipmethodStatus, monitorportalShipmethodStatus, monitorportalShipmethodCallRate):
    data = preprocessdata(shipmethods, atropsShipmethodStatus, monitorportalShipmethodStatus, monitorportalShipmethodCallRate)
    headers = ['Shipmethod', 'Atrops', "Monitotportal", "Call Rates"]
    table = getPrintableTable(data, headers)
    print(table)

if __name__ == "__main__":
    printColoured(f"\nHello, you logged in as  {getpass.getuser()}", "green")
    printColoured(f"[INFO]: Authentication going on for user {getpass.getuser()} ...", "green")
    auth = Authentication()
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
    printColoured("[INFO]: --------- Starting the Atrops calls ---------", "green")
    atropsShipmethodStatus = getActiveInactiveFromAtrops(session, carrierData, shipmethods)
    printColoured("[INFO]: --------- Starting the MonitorPortal calls ---------", "green")
    monitorportalShipmethodCallRate = getNDayCallRateFromMonitorportal(session, carrierData, shipmethods)
    monitorportalShipmethodStatus = getShipmethodStatus(monitorportalShipmethodCallRate);
    filename = "ActiveInactive_" + str(int(time.time())) +".xlsx"
    makeworkbook(filename, shipmethods, atropsShipmethodStatus, monitorportalShipmethodStatus, monitorportalShipmethodCallRate)
    printTable(shipmethods, atropsShipmethodStatus, monitorportalShipmethodStatus, monitorportalShipmethodCallRate)
    printColoured(f"\n[INFO]: Workbook with name {filename} has been created\n", "green")
