import openpyxl
from pathlib import Path
import applicationsConstants as ApplicationsConstants

def getShipmethodsFromExcel(session, carrierData):
    carrierListFile = Path(ApplicationsConstants.CARRIER_LIST_EXCEL_FILE_NAME)
    workbookObj = openpyxl.load_workbook(carrierListFile)
    workbookSheet = workbookObj[carrierData.region]
    shipmethodDict = {}
    tempList = [list()]
    for row in workbookSheet.iter_rows():
        if row[0].value == None:
            tempList.append(list())
        else:
            tempList[-1].append(row[0].value)
    for list_ in tempList:
        shipmethodDict[list_[0]] = list_[1:]
    if carrierData.carrier in shipmethodDict:
        return shipmethodDict[carrierData.carrier]
    return list()