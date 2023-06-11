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
    s = """  aws tickety --region us-west-2 --endpoint-url https://us-west-2.api.tickety.amazon.dev create-ticket --ticket '{"title": "test ticket", "severity": "SEV_5", "description":"description","categorization": [{"key": "category", "value":"Ticketing"}, {"key": "type", "value":"Wonka"}, {"key": "item","value":"Integration Tests"} ] }' --aws-account-id 474955757919 --ticketing-system-name Default"""
    proc = subprocess.Popen([s], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    out = out.decode("utf-8")


class Find_Team(Resource):
    def post(self):
        # abort_if_todo_doesnt_exist(question)
        print(request.get_json()["message"])
        return {"Response":return_ticket(request.get_json()["message"])[0]}


api.add_resource(Find_Team, '/Find_Team/')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')