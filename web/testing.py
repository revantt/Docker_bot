import sys
import getpass
import urllib3
from g2s2Accessor import G2S2Accessor
from temporaryUtils import *
from carrierData import CarrierData
from authentication import Authentication
from applicationsConstants import REGION_SUPPORTED

# To disable unverified HTTPS request is being made to host.
urllib3.disable_warnings()

# To not generate the bytecode i.e. .pyc files.
sys.dont_write_bytecode = True
status = ["FULLY_LAUNCHED","PARTIALLY_LAUNCHED"]

"""
x = re.findall(r'[0-9]+[A-Z]+',s)
y = re.findall(r'[0-9]+(?:[-_][0-9]+)+',s)
z = list(set(y) - set([i[:-2] for i in x])) + x
https://g2s2-editor.amazon.com/editor/g2s2?url=metadata/selfserve_carrier_weblab_config_table/?stage_version=@selfserve_carrier_weblab_configProd%26next_gen_shipmethod_name=ARAS_STD_DOM
"""

def getSelfServeStatus(Shipmethod,session):
    g2s2 = G2S2Accessor()
    payload_dict = {"next_gen_shipmethod_name":Shipmethod}
    g2s2_payload = g2s2.getG2S2TableData(session,"selfserve_carrier_weblab_config_table",
                                         payload_dict,
                                         "selfserve_carrier_weblab_configProd"
                                         )
    return g2s2_payload

if __name__ == "__main__":
    # printColoured(f"\nHello, you logged in as  {getpass.getuser()}", "green")
    # printColoured(f"[INFO]: Authentication going on for user {getpass.getuser()} ...", "green")
    auth = Authentication(maxRedirects=15)
    auth.sentryAuthentication()
    printColoured("[INFO]: Sentry authentication done !!", "green")
    auth.midwayAuthentication()
    printColoured("[INFO]: Midway authentication done !!", "green")
    session = auth.session
    scannbleId = "230124115601036198243880224AZ"
    shipmentid = "353629759"
    # scannbleId = input("Ether the orderID \n")
    for i in REGION_SUPPORTED:
        carrierData = CarrierData("", i, "", False)
        eagleeye = EagleEye(carrierData)
        eagleEyeResponse = eagleeye.getEagleEyeResponseShipment(session, shipmentid)
        Shipmethod = eagleeye.getShipmethod(eagleEyeResponse)
        if Shipmethod != None:
            print(Shipmethod)
            break
    if Shipmethod != None:
        result = getSelfServeStatus(Shipmethod,session)
        if result["totalResultSize"] == "1":
            temp = result["payload"][0]["ionPayload"]
            for s in status:
                if s in temp:
                    print("Self serve status",s)
                    break
        else:
            print("Self serve status," "NOT_LAUNCHED")