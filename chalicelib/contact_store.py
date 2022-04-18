import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
import logging
class ContactStore:
    def __init__(self, store_location):
        self.table = boto3.resource(
            'dynamodb', 'ca-central-1').Table(store_location)

    def save_contact(self, contact_info):
        try:
            response = self.table.put_item(Item=contact_info)
            # should return values from dynamodb however,
            # dynamodb does not support ReturnValues = ALL_NEW
            return contact_info
        except ClientError as ce:
            logging.error(ce)
            return "Error inserting to Collection"

    def get_all_contacts(self):
        try:
            response = self.table.scan()
        except ClientError as ce:
            logging.error(ce)
            return "Error Retrieving from Collection"
            

        contact_info_list = []
        for item in response['Items']:
            contact_info_list.append(item)

        return contact_info_list

    def get_contact_by_name(self, name):
        try:
            response = self.table.scan(
            FilterExpression=Attr("name").contains(name)
        )
        except ClientError as ce:
            logging.error(ce)
            return "Error Retrieving from Collection"


        if 'Items' in response:
            contact_info = response['Items']
        else:
            contact_info = {}

        return contact_info
