# coding=utf-8
# flake8: noqa E402

import logging
import typing
from uuid import UUID
from eventsourcing.application import AggregateNotFound
from flask import Flask, Response, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity  # type: ignore
from flask_restful import reqparse, Resource, Api  # type: ignore
from eventsourcing.system import System
from banking.applicationmodel import AccountNotFoundError, Bank
# from banking.domainmodel import UserAggregate
from banking.applicationmodel import UserApplication
from uuid import uuid4

app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret"

api = Api(app, prefix="/api/v1")

_bank = Bank()

def bank() -> Bank:
    return _bank


class User:
    id: str


def user() -> User:
    return User()  # return current api user logged in



class SignupResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'username', type=str, required=True, help='Username cannot be blank')
        self.parser.add_argument(
            'email', type=str, required=True, help='Email cannot be blank')
        self.parser.add_argument(
            "password", type=str, required=True, help="Password cannot be blank"
        )

    def post(self):
        data = self.parser.parse_args()
        user_application = UserApplication()
        data["id"] = str(uuid4())
        id = user_application.add_user(data)
        return {'message': 'User registered successfully', "id": id}, 201
       


class AccountResource(Resource):
    @jwt_required()
    def get(self) -> typing.Dict[str, typing.Any]:
        logging.info("account get")
        account = bank().get_account(UUID(user().id))
        return {
            "balance": str(account.balance),
            "identity": user().id,
        }


api.add_resource(AccountResource, "/account")
api.add_resource(SignupResource, '/signup')
