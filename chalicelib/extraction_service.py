import boto3
from collections import defaultdict
import usaddress
from botocore.exceptions import ClientError
import logging

class ExtractionService:
    def __init__(self):
        self.comprehend = boto3.client('comprehend')
        self.comprehend_med = boto3.client('comprehendmedical')

    def extract_contact_info(self, contact_string):
        contact_info = defaultdict(list)

        # extract info with comprehend
        try:
            response_comprehend = self.comprehend.detect_entities(
            Text=contact_string,
            LanguageCode='en'
        )
        except ClientError as ce:
            logging.error(ce)
            return "Error detecting entities from Comprehend"
        name_comprehend = []
        for entity in response_comprehend['Entities']:
            if entity['Type'] == 'PERSON':
                name_comprehend.append(entity['Text'])
            elif entity['Type'] == 'ORGANIZATION':
                contact_info['organization'].append(entity['Text'])

        # extract info with comprehend medical
        try:
            response = self.comprehend_med.detect_phi(
            Text=contact_string
        )
        except ClientError as ce:
            logging.error(ce)
            return "Error detecting entities from Medical Comprehend"
        if len(name_comprehend) > 1:
            contact_info["title"].append(name_comprehend[-1])

        for entity in response['Entities']:
            if entity['Type'] == 'EMAIL':
                contact_info['email'].append(entity['Text'])
            elif entity['Type'] == 'PHONE_OR_FAX':
                contact_info['phone'].append(entity['Text'])
            elif entity['Type'] == 'NAME':
                contact_info['name'].append(entity['Text'])

            elif entity['Type'] == 'ADDRESS':
                contact_info['address'].append(entity['Text'])

        # additional processing for address
        address_string = ' '.join(contact_info['address'])
        try:
            address_parts = usaddress.parse(address_string)
        except ClientError as ce:
            logging.error(ce)
            return "Error in parsing address"

        for part in address_parts:
            if part[1] == 'PlaceName':
                contact_info['city'].append(part[0])
            elif part[1] == 'StateName':
                contact_info['state'].append(part[0])
            elif part[1] == 'ZipCode':
                contact_info['zip'].append(part[0])

        return dict(contact_info)
