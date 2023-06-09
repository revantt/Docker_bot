import pathlib
SPACE = ' '
NEW_LINE = "\n"
EMPTY_STRING = ""
MAX_RETRIES = 25
CARRIER_LIST_EXCEL_FILE_NAME = "CarrierList.xlsx"
CONNECTION_ERROR_MESSAGE = "Failed to establish a new connection, If you work for Amazon, you must use Amazon Enterprise Access (AEA)" \
    "to reach this site. If you don’t work for Amazon, you’ve been mistakenly directed to an internal-only Amazon system." \
    "Please contact the source of this link and request a corrected link."
FORBIDDEN_ERROR_MESSAGE = "Forbidden error occurred, If you work for Amazon, you must use Amazon Enterprise Access (AEA)" \
    "to reach this site. If you don’t work for Amazon, you’ve been mistakenly directed to an internal-only Amazon system." \
    "Please contact the source of this link and request a corrected link."
EMPTY_LIST = list()
EMPTY_DICT = dict()
NA_REGION_CODE = "NA"
EU_REGION_CODE = "EU"
CN_REGION_CODE = "CN"
FE_REGION_CODE = "FE"
NRT_REGION_CODE = "NRT"
FIVE_YEAR_DAYS = 1825
DOUBLE_NEW_LINE = "\n\n"
MILISECONDS_IN_DAY = 86400000
masterFile = "masterSheet.xlsx"
KIBANA_TLGS_REQUEST_INDEX = "lair-gts-tlgs-req*"
G2S2_BASE_URL = "https://g2s2-editor.amazon.com/editor/"
TRANS_LABEL_GENERATION_SERVICE = "TransLabelGenerationService"
REGION_SUPPORTED = [NA_REGION_CODE, EU_REGION_CODE, CN_REGION_CODE, FE_REGION_CODE]
SENTRY_BASE_URL = "https://sentry.amazon.com/sentry-braveheart?value=1"
ISENGARD_SERVICE_BASE_URL = "https://isengard-service-beta.amazon.com"
ATROPS_BASE_URL = "https://atrops-web-na.amazon.com/warehouse_data/"
MONITORPORTAL_BASE_URL = "https://monitorportal.amazon.com/igraph/"
MONITORPORTAL_GET_GRAPH_DATA_BASE_URL = "https://monitorportal.amazon.com/mws?Action=GetGraph&Version=2007-07-07&DataSet=Prod" \
    "&HostGroup=ALL&Host=ALL&MethodName=ALL&Client=ALL&MetricClass=NONE&Instance=NONE&Stat=n"
G2S2_BASE_URL = "https://g2s2-editor.amazon.com/editor/"
LABEL_TEMPLATES_PACKAGE_NAME = "LabelTemplates"
G2S2_ANALYSIS_FILE_EXTENSION = "_G2S2Analysis.xlsx"
GET_LABEL_BY_ID = "GetLabelById"
AMAZON_DRIVE_BASE_URL = "https://drive.corp.amazon.com/"
LABELARY_API_BASE_URL = "http://api.labelary.com/v1/printers/"
COMPARISON_RESULT_DRIVE_FOLDER = "labelComparisonResults"
EXPECTED_LABELS_DIR_NAME = "expectedLabels"
ACTUAL_LABELS_DIR_NAME = "actualLabels"
EXPECTED_LABEL_DRIVE_FOLDER = f'{COMPARISON_RESULT_DRIVE_FOLDER}/{EXPECTED_LABELS_DIR_NAME}_'
ACTUAL_LABEL_DRIVE_FOLDER = f'{COMPARISON_RESULT_DRIVE_FOLDER}/{ACTUAL_LABELS_DIR_NAME}_'
EXPECTED_LABEL_LOCAL_FOLDER = f'{pathlib.Path(__file__).parent.resolve()}/{EXPECTED_LABELS_DIR_NAME}/'
ACTUAL_LABEL_LOCAL_FOLDER = f'{pathlib.Path(__file__).parent.resolve()}/{ACTUAL_LABELS_DIR_NAME}/'
ZPL_LABEL_TYPE = "ZPL"
PNG_LABEL_TYPE = "PNG"
PDF_LABEL_TYPE = "PDF"
UPLOADING_LABEL_WORKERS = 24
GENERATE_LABEL_WORKERS = 24