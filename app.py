from crypt import methods
from chalice import Chalice
from inquirer import password
from matplotlib.pyplot import connect
from chalicelib import recognition_service
from chalicelib import extraction_service
from chalicelib import contact_store

import db

import base64
import json
import uuid


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
    request_data = json.loads(app.current_request.raw_body)
    file_name = request_data['filename']
    file_bytes = base64.b64decode(request_data['filebytes'])

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
    request_data = json.loads(app.current_request.raw_body.lower())

    for i in request_data.keys():
        if type(request_data[i]) is list:
            request_data[i] = [j.lower() for j in request_data[i]]
        else:
            request_data[i] = request_data[i].lower()

    # contact = contact_store.save_contact(request_data)

    return request_data


@app.route('/contacts/find', methods=['GET'], cors=True)
def get_all_contacts():
    request_data = json.loads(app.current_request.raw_body)
    name = request_data["name"]
    """gets all saved contacts in the contact store service"""
    #name= "GRILL CHRIS SALCEDO"
    contacts = contact_store.get_contact_by_name(name)
    return contacts


@app.route("/register", methods=["POST"], cors=True)
def registration():
    request_data = json.loads(app.current_request.raw_body)
    try:
        firstname = request_data["firstname"].lower()
        email = request_data["email"].lower()
        lastname = request_data["lastname"].lower()
        password = request_data["password"]

    except:
        return "Some fields are missing. Please enter all the required fields."

    id = "user_" + str(uuid.uuid1())

    user = {
        "id": id,
        "firstname": firstname,
        "email": email,
        "lastname": lastname,
        "password": password
    }
    response = db.add_user(user)

    return response


@app.route("/login", methods=["POST"], cors=True)
def login():
    request_data = json.loads(app.current_request.raw_body)

    try:
        email = request_data["email"].lower()
        passowrd_given = request_data["password"]

    except:
        return "Please provide all the fields."

    user = db.get_user(email)

    if len(user) == 0:
        return "Please register and then try logging in. "
    else:
        user = user[0]
        if passowrd_given != user["password"]:
            return "Please provide correct password"
        else:
            return {"user_id": user["id"], "message": "Login Success", "user_firstname": user["firstname"]}


@app.route("/sample", methods=["POST"], cors=True)
def sample():

    return
