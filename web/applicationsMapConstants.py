from applicationsConstants import NA_REGION_CODE, FE_REGION_CODE, CN_REGION_CODE, EU_REGION_CODE
REGION_SUPPORTED = [NA_REGION_CODE, EU_REGION_CODE, CN_REGION_CODE, FE_REGION_CODE]
KIBANA_NOT_SUPPORTED_REGIONS = [CN_REGION_CODE]
AUTHENTICATION_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=UTF-8",
    "Content-Encoding": "amz-1.0",
    "X-Amz-Target": "IsengardService.Hello"}
ORGS = {
    NA_REGION_CODE: ["BR", "CA", "MX", "US", "US-AE"],
    EU_REGION_CODE: ["AE", "DE", "EG", "ES", "FR", "GB", "IN", "IT", "NL", "PL", "SA", "SE", "TR", "UK-AE"],
    CN_REGION_CODE: [],
    FE_REGION_CODE: ["AU", "JP", "JP-AE", "SG"]}
KIBANA_HEADERS = {
    "Accept":"application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-ndjson",
    "kbn-version": "6.8.1"}
TCDA_HEADERS = {
    "Accept":"application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Content-Type": "application/json; charset=UTF-8",
    'User-Agent':'test'}
MARKETPLACE = {
    NA_REGION_CODE: ["USAmazon"],
    EU_REGION_CODE: ["EUAmazon"],
    CN_REGION_CODE: ["CNAmazon"],
    FE_REGION_CODE: ["NRTAmazon", "JPAmazon", "FEAmazon"]}
TRANS_LOGISTICS_URL = {
    NA_REGION_CODE: "https://trans-logistics.amazon.com/ccs/",
    EU_REGION_CODE: "https://trans-logistics-eu.amazon.com/ccs/",
    CN_REGION_CODE: "https://trans-logistics-cn.amazon.com/ccs/",
    FE_REGION_CODE: "https://trans-logistics-fe.amazon.com/ccs/"}
KIBANA_URL = {
    NA_REGION_CODE: "https://lair-na.corp.amazon.com/",
    EU_REGION_CODE: "https://lair-eu.corp.amazon.com/",
    FE_REGION_CODE: "https://lair-fe.corp.amazon.com/"}
SHIPPING_LABEL = {
    NA_REGION_CODE: ["AFN_CA", "HQ_CA", "AFN_US", "NA_SHIPPING_LABEL", "HQ_GLOBAL_HAZMAT_LABEL", \
        "AFN_GLOBAL_HAZMAT_LABEL", "GLOBAL_SHIPPING_LABEL"],
    EU_REGION_CODE: ["EU_SHIPPING_LABEL", "HQ_GLOBAL_HAZMAT_LABEL", "AFN_GLOBAL_HAZMAT_LABEL", "GLOBAL_SHIPPING_LABEL"],
    FE_REGION_CODE: ["FE_SHIPPING_LABEL", "HQ_GLOBAL_HAZMAT_LABEL", "AFN_GLOBAL_HAZMAT_LABEL", "GLOBAL_SHIPPING_LABEL"],
    CN_REGION_CODE: ["CN", "CN_SHIPPING_LABEL", "HQ_GLOBAL_HAZMAT_LABEL", "AFN_GLOBAL_HAZMAT_LABEL", "GLOBAL_SHIPPING_LABEL"]}
EAGLE_EYE_URL = {
    NA_REGION_CODE: "https://eagleeye-na.amazon.com/",
    EU_REGION_CODE: "https://eagleeye-eu.amazon.com/",
    FE_REGION_CODE: "https://eagleeye-fe.amazon.com/",
    CN_REGION_CODE: "https://eagleeye-cn.amazon.com/"}
CIT_NEW_MASTER_URL = {
    NA_REGION_CODE: "https://cit-new-master-iad.iad.proxy.amazon.com/",
    EU_REGION_CODE: "https://cit-new-master-dub.dub.proxy.amazon.com/",
    FE_REGION_CODE: "https://cit-new-master-nrt.nrt.proxy.amazon.com/",
    CN_REGION_CODE: "https://cit-new-master-pek.pek.proxy.amazon.com/"}
TAXONOMY_URL = {
    NA_REGION_CODE: "https://transportation-taxonomy-iad.aka.amazon.com/",
    EU_REGION_CODE: "https://transportation-taxonomy-dub.aka.amazon.com/",
    FE_REGION_CODE: "https://transportation-taxonomy-pdx.aka.amazon.com/",
    CN_REGION_CODE: "https://transportation-taxonomy-pek.aka.amazon.com/"}
TAXONOMY_GAMMA_URL = {
    NA_REGION_CODE: "https://transportation-taxonomy-iad-gamma.aka.amazon.com/",
    EU_REGION_CODE: "https://transportation-taxonomy-dub-gamma.aka.amazon.com/",
    FE_REGION_CODE: "https://transportation-taxonomy-pdx-gamma.aka.amazon.com/",
    CN_REGION_CODE: "https://transportation-taxonomy-pek-gamma.aka.amazon.com/"}
LABELARY_PDF_HEADERS = {'Accept' : 'application/pdf'}

NA_REGION_CODE = ["BR", "CA", "MX", "US", "US-AE"]
EU_REGION_CODE = ["AE", "DE", "EG", "ES", "FR", "GB", "IN", "IT", "NL", "PL", "SA", "SE", "TR", "UK-AE"]
CN_REGION_CODE = []
FE_REGION_CODE = ["AU", "JP", "JP-AE", "SG"]