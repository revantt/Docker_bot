from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
from main import return_ticket
from GetContainer import returnSelfServeStatus
from flask_cors import CORS
import subprocess


app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()

def cut_ticket(payload):
    description = payload["desc"]
    impact = payload["impactedShipment"]
    shipment = payload["shipmentsExample"]
    # s = """  aws tickety --region us-west-2 --endpoint-url https://us-west-2.api.tickety.amazon.dev create-ticket --ticket '{"title": "test ticket", "severity": "SEV_5", "description":"description","categorization": [{"key": "category", "value":"Ticketing"}, {"key": "type", "value":"Wonka"}, {"key": "item","value":"Integration Tests"} ] }' --aws-account-id 474955757919 --ticketing-system-name Default"""
    final_desc = "Description of issue -- \\n"  + description  + "\\n Impact of the severity --" + impact + "\\n Shipment(s) impacted--  \\n" + "  ".join(shipment)
    s = """  aws tickety --region us-west-2 --endpoint-url https://us-west-2.api.tickety.amazon.dev create-ticket --ticket '{"title": "test ticket", "severity": "SEV_5", "description": " """ + str(final_desc) + """ ","categorization": [{"key": "category", "value":"Ticketing"}, {"key": "type", "value":"Wonka"}, {"key": "item","value":"Integration Tests"} ] }' --aws-account-id 474955757919 --ticketing-system-name Default"""
    proc = subprocess.Popen([s], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    out = out.decode("utf-8")
    return out


class Find_Team(Resource):
    def post(self):
        # abort_if_todo_doesnt_exist(question)
        print(request.get_json()["desc"])
        payload = request.get_json()
        print(payload["shipmentsExample"])
        try:
            resp, ret = return_ticket(payload["desc"])
            if ret == 1:
                result = {"Response": return_ticket(resp)[0],
                        "SelfServeStatus" : returnSelfServeStatus(payload["shipmentsExample"][0],True)
                      }
            else:
                result = {"Response": return_ticket(resp)[0],
                        "SelfServeStatus" : ""
                      }

            return result
        except Exception as e:
            return {"Response": "Some error occured " + e}
        # return {"Response":return_ticket(request.get_json()["desc"])[0]}


class Cut_Ticket(Resource):
    def post(self):
        payload = request.get_json()
        Result = {"Response": cut_ticket(payload)}
        return Result

        cut_ticket(payload)

api.add_resource(Find_Team, '/Find_Team/')
api.add_resource(Cut_Ticket, '/Cut_Ticket/')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')