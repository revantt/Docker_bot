from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
from main import return_ticket
from GetContainer import returnSelfServeStatus
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()

class Find_Team(Resource):
    def post(self):
        # abort_if_todo_doesnt_exist(question)
        print(request.get_json()["message"])
        return {"Response":return_ticket(request.get_json()["message"])[0]}


api.add_resource(Find_Team, '/Find_Team/')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')