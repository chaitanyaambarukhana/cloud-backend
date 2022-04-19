
from chalice import Chalice
from chalicelib import recognition_service
from chalicelib import extraction_service
from chalicelib import contact_store

import chalicelib.user_service as user_service

import base64
import json
import uuid

from botocore.exceptions import ClientError
import logging
#####
# chalice app configuration
#####
app = Chalice(app_name='Capabilities')
app.debug = True

#####
# services initialization
#####
recognition_service = recognition_service.RecognitionService()
extraction_service = extraction_service.ExtractionService()
store_location = 'contacts'
contact_store = contact_store.ContactStore(store_location)


#####
# RESTful endpoints
#####
@app.route('/extract-info', methods=['POST'], cors=True)
def upload_image():
    """processes file upload and saves file to storage service"""
    MIN_CONFIDENCE = 70.0
    
    try:
        request_data = json.loads(app.current_request.raw_body)
            #file_name = request_data['filename']
        file_bytes = base64.b64decode(request_data['filebytes'])
    except ClientError as ce:
            logging.error(ce)
            return "Bad Request"

    text_lines = recognition_service.detect_text(file_bytes)

    contact_lines = []
    for line in text_lines:
        # check confidence
        if float(line['confidence']) >= MIN_CONFIDENCE:
            contact_lines.append(line['text'])

    contact_string = '   '.join(contact_lines)
    contact_info = extraction_service.extract_contact_info(contact_string)

    return contact_info

@app.route('/contacts', methods=['POST'], cors=True)
def save_contact():
    """saves contact information to the contact store service"""
    try:
        request_data = json.loads(app.current_request.raw_body.lower())
    except ClientError as ce:
            logging.error(ce)
            return "Bad Request"

    if "contact_id" not in request_data.keys():
        contact_id = "contact_" + str(uuid.uuid1())
        request_data["contact_id"] = contact_id

    for i in request_data.keys():
        if type(request_data[i]) is list:
            request_data[i] = [j.lower() for j in request_data[i]]
        else:
            request_data[i] = request_data[i].lower()

    contact = contact_store.save_contact(request_data)

    return contact


@app.route('/contacts/find', methods=['POST'], cors=True)
def get_all_contacts():
    try:
        request_data = json.loads(app.current_request.raw_body)
    except ClientError as ce:
            logging.error(ce)
            return "Bad Request"
    name = request_data["name"].lower()
    """gets all saved contacts in the contact store service"""
    #name= "GRILL CHRIS SALCEDO"
    contacts = contact_store.get_contact_by_name(name)
    return contacts

# get contacts by id


@app.route("/get-contact", methods=["POST"], cors=True)
def get_contact():
    try:
        request_data = json.loads(app.current_request.raw_body)
    except ClientError as ce:
            logging.error(ce)
            return "Bad Request"

    contact_id = request_data["contact_id"]

    contact = user_service.get_contact(contact_id)

    return contact

# get contacts by user


@app.route("/get-user-contacts", methods=["POST"], cors=True)
def get_user_contacts():
    try:
        request_data = json.loads(app.current_request.raw_body)
    except ClientError as ce:
            logging.error(ce)
            return "Bad Request"
    user_id = request_data["user_id"]

    user_contacts = user_service.get_user_contacts(user_id)

    return user_contacts


@app.route("/register", methods=["POST"], cors=True)
def registration():
    try:
        request_data = json.loads(app.current_request.raw_body)
    except ClientError as ce:
            logging.error(ce)
            return "Bad Request"
    try:
        firstname = request_data["firstname"].lower()
        email = request_data["email"].lower()
        lastname = request_data["lastname"].lower()
        password = request_data["password"]
        if "role" not in request_data["role"]:
            role = "user"

    except:
        return "Some fields are missing. Please enter all the required fields."

    id = "user_" + str(uuid.uuid1())

    user = {
        "id": id,
        "firstname": firstname,
        "email": email,
        "lastname": lastname,
        "password": password,
        "role": role
    }
    response = user_service.add_user(user)

    return response


@app.route("/login", methods=["POST"], cors=True)
def login():
    try:
        request_data = json.loads(app.current_request.raw_body)
    except ClientError as ce:
            logging.error(ce)
            return "Bad Request"

    try:
        email = request_data["email"].lower()
        passowrd_given = request_data["password"]

    except:
        return "Please provide all the fields."

    user = user_service.get_user(email)

    if len(user) == 0:
        return "Please register and then try logging in. "
    else:
        user = user[0]
        if passowrd_given != user["password"]:
            return "Please provide correct password"
        else:
            return {"user_id": user["id"],"role":user['role'], "message": "Login Success", "user_firstname": user["firstname"]}


@app.route("/get-all-data", methods=["POST"],cors=True)
def get_all_data():
    try:
        request_data = json.loads(app.current_request.raw_body)
    except ClientError as ce:
            logging.error(ce)
            return "Bad Request"
    user = user_service.get_user_id(request_data["user_id"])[0]
    if user["role"] == "admin":
        response = user_service.get_all_data()
        return response["Items"]
    else:
        return "Requires Admin privilige"


@app.route("/delete-contact", methods=['DELETE'], cors=True)
def delete_contact():
    try:
        request_data = json.loads(app.current_request.raw_body)
    except ClientError as ce:
            logging.error(ce)
            return "Bad Request"
    contact_id = request_data["contact_id"]
    response = user_service.delete_contact(contact_id)
    return response


# @app.route("/sample", methods=["POST"], cors=True)
# def sample():

#     return
