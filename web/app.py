from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
from main import return_ticket

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

class Find_Team(Resource):
    def post(self):
        # abort_if_todo_doesnt_exist(question)
        print(request.form["message"])
        return {"Response":return_ticket(request.form["message"])[0]}

api.add_resource(Find_Team, '/Find_Team/')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')