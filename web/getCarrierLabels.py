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

urllib3.disable_warnings()
sys.dont_write_bytecode = True

def makeworkbookWithLabelImages(filename, imageStreams):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("Labels")
    headerFormat = workbook.add_format({'bold': True, 'fg_color': '3DD4F5', 'align': 'center', 'valign': 'vcenter'})
    worksheet.set_column('A:A', 40)
    worksheet.set_column('B:B', 80)
    templatemappingHeader = ["ShipMethod", "Label Image"]
    worksheet.write_row(0, 0, templatemappingHeader, headerFormat)
    row = 1
    for shipmethod in imageStreams:
        drivelink = "https://drive.corp.amazon.com/documents/" + getpass.getuser() + "@/" + driveDirName + shipmethod + ".jpg"
        worksheet.write(row, 0,  shipmethod)
        if imageStreams[shipmethod] != "":
            worksheet.write(row, 1,  drivelink)
        else:
            worksheet.write(row, 1,  "-")
        row += 1
    workbook.close()

if __name__ == "__main__":
    printColoured(f"\nHello, you logged in as  {getpass.getuser()}", "green")
    printColoured(f"[INFO]: Authentication going on for user {getpass.getuser()} ...", "green")
    auth = Authentication(maxRedirects=50)
    auth.sentryAuthentication()
    printColoured("[INFO]: Sentry authentication done !!", "green")
    auth.midwayAuthentication()
    printColoured("[INFO]: Midway authentication done !!", "green")
    session = auth.session
    carrier, region, orgs = getCarrierRegionOrg()
    carrierData = CarrierData(carrier, region, orgs, False)
    printColoured("Fetching ship methods ...", "green")
    shipmethods = getShipmethods(session, carrierData)
    printColoured(f"[INFO]: Number of ship method available: {len(shipmethods)}", "green")
    if len(shipmethods) == 0:
        printColoured(f"[WARN]: Zero shipmethod found for carrier: {carrierData.carrier}", "yellow")
        sys.exit()
    imageStreams = getLabelStreams(session, carrierData, shipmethods)
    driveDirName = carrier + "_LABELS/"
    makeNewDirInDrive(driveDirName)
    print("Created new directory in drive with name ", driveDirName)
    uploadImagesOnDrive(driveDirName, imageStreams)
    print("All Label images are uploaded in drive folder ", driveDirName)
    filename = carrierData.carrier + "labels_" + str(int(time.time())) +".xlsx"
    makeworkbookWithLabelImages(filename, imageStreams)
    print("\nWorkbook with name", filename, "has been created\n")
