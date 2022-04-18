import logging
import boto3 as aws
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr


def connect_db(tablename: str):
    try:
        client = aws.resource("dynamodb","ca-central-1").Table(tablename)
    except ClientError as ce:
        return ce

    return client


def add_user(user):
    table = connect_db("users")
    table_items = table.scan(
        FilterExpression=Attr("email").eq(user["email"])
    )

    if len(table_items["Items"]) != 0:
        return "User with the email already exists. Please try another email."

    response = table.put_item(
        Item=user
    )

    return response


def get_user(email:str):
    table = connect_db("users")
    try:
        user = table.scan(
            FilterExpression = Attr("email").eq(email)
        )["Items"]
        return user
    except ClientError as ce:
        logging.error(ce)
        return "User cannot be found"


def get_contact(contact_id):
    table = connect_db("users")
    
    try:
        contact = table.scan(FilterExpression = Attr("contact_id").eq(contact_id))["Items"]
        return contact
    except:
        return "Contact Doesnot exist"
    
    