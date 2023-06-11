from GLOBAL_TOKENS import *
from GetContainer import returnSelfServeStatus
import spacy
import re
labeling_tokens = Labeling().Tokens
upps_tokens = Upps().Tokens
crs_tokens = CRS().Tokens
idgs_tokens = IDGS().Tokens
teams = ["Labeling","UPPS","CRS","IDGS"]
tokens = [labeling_tokens,upps_tokens,crs_tokens,idgs_tokens]
token_mapping = dict(zip(teams,tokens))
nlp = spacy.load('en_core_web_sm')
key_weight = {i:(2 if i in labeling_tokens else 1) for i in upps_tokens+crs_tokens+idgs_tokens+labeling_tokens}
"""
UPPS : https://sim.amazon.com/issues/create?assignedFolder=27d68c69-8907-4d38-810d-4a2096bb97a1
CRS : https://sim.amazon.com/issues/create?assignedFolder=6454d593-8767-4d2b-af7d-04194fe7ca4c
Labelling : https://sim.amazon.com/issues/create?assignedFolder=6d68f286-6c11-41b9-ae3a-0400ad224eee
IDGS : https://sim.amazon.com/issues/create?assignedFolder=32d4b089-1670-4f6e-a0d6-5de01582e538
"""

CTT = {
    "Labeling" : "https://sim.amazon.com/issues/create?assignedFolder=6d68f286-6c11-41b9-ae3a-0400ad224eee",
    "UPPS" : "https://sim.amazon.com/issues/create?assignedFolder=27d68c69-8907-4d38-810d-4a2096bb97a1",
    "CRS" : "https://sim.amazon.com/issues/create?assignedFolder=6454d593-8767-4d2b-af7d-04194fe7ca4c",
    "IDGS" : "https://sim.amazon.com/issues/create?assignedFolder=32d4b089-1670-4f6e-a0d6-5de01582e538"
}
def allot_team(query):
    query = query.lower()
    vote_dict = {i: 0 for i in teams}
    max_vote = 0
    max_vote_team = ""
    doc = nlp(query)
    lemma = [i.lemma_ for i in doc]
    final_string = " ".join(lemma)
    print(final_string)
    for i in teams:
        for j in token_mapping[i]:
            if j in final_string:
                intent = j
                vote_dict[i] += key_weight[j]
        if vote_dict[i] >= max_vote:
            max_vote = vote_dict[i]
            max_vote_team = i
    print(vote_dict)
    # print(vote_dict,key_weight)
    if max_vote == 0:
        return "Be more specific please",0
    if max_vote_team == "UPPS":
        x = re.findall(r'[0-9]+[a-z]+', query)
        y = re.findall(r'[0-9]+(?:[-_][0-9]+)*', query)
        z = list(set(y) - set([i[:-2] for i in x])) + x
        shipmentStatus = "shipment" not in query
        result_list = {t:returnSelfServeStatus(t.upper(),shipmentStatus) for t in z}
        print(result_list,shipmentStatus,x,y)
        if any(result_list.values()):
            return "UPPS",1
        else:
            return "Labeling",1

    return max_vote_team,1

def return_ticket(query):
    return allot_team(query)


