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

""" To print the data in the table format """
def printTable(monitorportalCarrierCallRate):
    data = list()
    for carrier in monitorportalCarrierCallRate:
        data.append([carrier, monitorportalCarrierCallRate[carrier]["oneDay"], "{:.7f}". format(monitorportalCarrierCallRate[carrier]["sevenDay"])])
    headers = ["Carrier Name", "One Day", "Seven Day"]
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
    carrierCount = 0
    carriersList = list()
    carrierCount = input("Enter number of carriers: ")
    while len(carriersList) != int(carrierCount):
        carrierName = input("Enter name of carrier: ")
        carrierRegion = input("Enter region for the carrier: ")
        carriersList.append(CarrierData(carrierName, carrierRegion, "", False))
    printColoured("[INFO]: --------- Starting the MonitorPortal calls ---------", "green")
    monitorportalCarrierCallRate = getCarrierCallRateFromMonitorportal(session, carriersList)
    printTable(monitorportalCarrierCallRate)
