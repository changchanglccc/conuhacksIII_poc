from flask import Flask, request, redirect
from flask_jsonpify import jsonify
from pymongo import mongo_client
import flask
import requests

import os
import time
import json

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"
# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
# SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
API_SERVICE_NAME = 'drive'
SCOPES=[
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
      ]
API_VERSION = 'v2'

from watson_developer_cloud import VisualRecognitionV3

# get a classifier
# visual_recognition = VisualRecognitionV3(
#     '2016-05-20',
#     api_key='7e6e8982b7d6857732e15f7625c296035191d8d7'
# )
# classifier = visual_recognition.get_classifier(
#     classifier_id='elderlyFallPain_700377303')
# print(json.dumps(classifier, indent=2))

# with open("/Users/chongli/Desktop/a.jpeg", 'rb') as images_file:
#     classes = visual_recognition.classify(
#         images_file,
#         parameters=json.dumps({
#             'classifier_ids': ['elderlyFallPain_700377303', 'default'],
#             'threshold': 0.2
#         }))
# result = json.dumps(classes, indent=2)
# print(result)
# value = classes['images'][0]['classifiers'][0]['classes'][0]['score']
# print(value)

app = Flask(__name__)

# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
#760668503313-1024oeh105l8te3voorffd3ckuk691jo.apps.googleusercontent.com
#rOidowp9-T5dXR2J8DM5536j
app.secret_key = 'rOidowp9-T5dXR2J8DM5536j'

######### Method
# Bind a camera to a detector
# def bind_camera_detector(user_id, camera_id, detector_name):
#     client = get_an_instance()
#     result = None
#     detector_id = client.local.users.find_one(
#         {'user_id': user_id, 'detector_name': detector_name}
#     )
#     if detector_id:
#         result = client.local.cameras.find_one(
#             {
#                 "user_id": user_id,
#                 "camera_id": camera_id
#             })
#         if result:
#             client.local.cameras.update_one(
#                 {
#                     'user_id': user_id,
#                     'camera_id': camera_id
#                 },
#                 {'$set': {'detector_id': detector_id['detector_id']}})
#         else:
#             client.local.cameras.insert_one(
#                 {'user_id': user_id,
#                  'camera_id': camera_id,
#                  'detector_id': detector_id['detector_id']}
#             )
#         result = detector_id['detector_name']
#         client.close()
#         return result
#     client.close()
#     return result

# Check if a camera belongs to a user. If not exists, insert one.
def insert_camera(camera_id, user_id):
    client = get_an_instance()
    result = client.local.cameras.find_one({'camera_id': camera_id, 'user_id': user_id})
    if not result:
        try:
            client.local.cameras.insert_one(
                {'user_id': user_id,
                 'camera_id': camera_id,
                 'detector_id': None}
            )
        except Exception:
            client.close()
            return False
    client.close()
    return True

# def get_keyword(detector_id):
#     client = get_an_instance()
#     target = client.local.detectors.find_one({'id': detector_id})
#     client.close()
#     return target['name']


# get the image of camera
def get_image(user_id, camera_id):
    client = get_an_instance()
    target = client.local.monitor.find_one({'user_id': user_id, 'camera_id': camera_id})
    client.close()
    return target['image_path']


# Get a database client instance
def get_an_instance():
    client = None
    try:
        client = mongo_client.MongoClient("mongodb://localhost:27017")
    except Exception:
        print("Database connection error.")
    return client

# Save the path of an image from a camera to database
def insert_image(user_id, camera_id, image_path):
    client = get_an_instance()
    exist = client.local.monitor.find_one({
        'user_id': user_id,
        'camera_id': camera_id
    })
    if exist:
        try:
            client.local.monitor.update_one(
                {
                    "user_id": user_id,
                    "camera_id": camera_id,
                },
                {
                    '$set': {'image_path': image_path}
                }
            )
            client.close()
            return True
        except Exception:
            client.close()
            return False
    else:
        try:
            client.local.monitor.insert_one(
                {
                    "user_id": user_id,
                    "camera_id": camera_id,
                    'image_path': image_path
                }
            )
            client.close()
            return True
        except Exception:
            client.close()
            return False

        # List all cameras of a user
def list_all_cameras(user_id):
    client = get_an_instance()
    result = client.local.cameras.find({'user_id': user_id})
    client.close()
    c_list = []
    print(result)
    if result:
        for c in result:
            name = ""#get_detector_name(user_id, c['detector_id'])
            c_list.append({'camera_id': c['camera_id'], 'detector_id': c['detector_id'], 'classifier_name': name})
        return c_list
    return 'Error: no camera found'
# Bind the detector to a user
# def bind_detector_user(user_id, detector_name, detector_id):
#     client = get_an_instance()
#     try:
#         client.local.users.insert_one(
#             {
#                 "user_id": user_id,
#                 "detector_name": detector_name,
#                 "detector_id": detector_id,
#                 "cameras": [],
#                 "status": "active"
#             }
#         )
#         client.close()
#         return True
#     except Exception:
#         return False

##################### Google auth

@app.route('/')
def hello():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    return redirect('http://ec2-18-217-218-155.us-east-2.compute.amazonaws.com/index.html', code=302)


@app.route('/<path:path>')
def static_file(path):
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    return app.send_static_file(path)


@app.route('/api')
def api_list():
    body = '''
        <!DOCTYPE html>
            <h1>POC REST API
            <p>
            alert condition: <a href="/rest/api/username/camera/12306/setting">/rest/api/user/camera/id/setting</a>
            <p>
            get camera list: <a href="/rest/api/username/camera">/rest/api/user/camera</a>
            <p>
            do a detection: <a href="/rest/api/detection">/rest/api/detection</a>
        </html>'''
    response = flask.Response(body)
    return response

# @app.route('/rest/api/camera/setting', methods=['GET', 'POST'])
# def alert_setting():
#     user_id = flask.session['email_address']
#     camera_id = request.form['camera_id']
#     detector_name = request.form['detector_name']
#     print("camera,name", camera_id, detector_name)
#     status = 42
#     description = 'Setting failed.'
#     detector_info = bind_camera_detector(user_id=user_id, camera_id=camera_id, detector_name=detector_name)
#     if detector_info:
#         status = 0
#         description = 'Setting completed.'
#
#     # setting = {
#     #     'camera_id': 12315,
#     #     'condition': {
#     #         'detector_id': 12345678901,
#     #         'human_name': "Bear",
#     #         'positive': False  # also could be True, means if then or if not then
#     #         }
#     # }
#
#     result = {
#         'results': {
#             'status': status,  # 0 is success, the others could be fault, reason in description
#             'description': description,
#             'camera_id': camera_id,
#             'detector': detector_info
#         }
#     }
#     return jsonify(result)

@app.route('/rest/api/camera', methods=['GET'])  # , 'POST'
def camera_list():
    user_id = flask.session['email_address']
    result = list_all_cameras(user_id)

    return jsonify(result)


# @app.route('/rest/api/release_camera', methods=['POST'])
# def release_camera():
#     user_id = 'u001'
#     camera_id = ['c002', 'c005']
#     client = get_an_instance()
#     client.local.cameras.find_one_and_update({'user_id': user_id, 'camera_id': camera_id},
#                                              {'$set': {'detector_id': ''}})
#     client.close()
#
# @app.route('/rest/api/register', methods=['POST'])
# def create_user():
#     user_id = 'u001'
#     password = '123'
#     client = get_an_instance()
#     try:
#         client.local.credentials.insert_one(
#             {
#                 "user_id": user_id,
#                 "password": password
#             }
#         )
#         client.close()
#         return 'Register completed.'
#     except Exception:
#         client.close()
#         return 'Register failed!'


@app.route('/rest/api/detection', methods=['GET', 'POST'])
def detector():
    if request.method == 'GET':
        body = '''
            <!DOCTYPE html>
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
                <title>Upload File</title>
                <h1>REST API Demo
                <p>
                <form method="POST" enctype="multipart/form-data">
                      <input type="file" id="imgInp" name="file">
                      <input type="submit" value="Upload">
                </form>
                <p>
                <img id="blah" src="#" alt="" height="50%" width="50%"/>
                <script>
                    function readURL(input) {

                    if (input.files && input.files[0]) {
                        var reader = new FileReader();

                        reader.onload = function(e) {
                          $('#blah').attr('src', e.target.result);
                        }

                        reader.readAsDataURL(input.files[0]);
                      }
                    }

                    $("#imgInp").change(function() {
                      readURL(this);
                    });
                </script>
            </html>'''
        response = flask.Response(body)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    elif request.method == 'POST':

        file = request.files['file']
        user_id = request.values['email']  # email
        camera_id = request.values['uuid']  # uuid
        print (user_id, camera_id)
        insert_camera(camera_id, user_id)
        print(list_all_cameras(user_id))

        base_folder = 'static/monitor/' + user_id + '/' + camera_id + '/'  # /Users/Ethan/Downloads/
        filename = 'monitor' + str(int(time.time())) + ".jpeg"
        alert_filename = 'alert_monitor' + str(int(time.time())) + '.jpeg'
        fullname = base_folder + filename
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)
        file.save(fullname)

        # detector_id = get_detector_by_camera(user_id, camera_id)
        # if not detector_id:
        #     insert_image(user_id, camera_id, fullname)
        #     response = flask.Response(json.dumps(result))
        #     response.headers['Access-Control-Allow-Origin'] = '*'  # This is important for Mobile Device
        #     return response
        # keyword = get_keyword(detector_id)
        # Classifying a picture from a file path
        print(fullname)
        # classification_result = api.classify_image(detector_id=detector_id, image_file=fullname)
        # print(classification_result)
        #######################  Classifier

        # get a classifier
        visual_recognition = VisualRecognitionV3(
            '2016-05-20',
            api_key='7e6e8982b7d6857732e15f7625c296035191d8d7'
        )
        # classifier = visual_recognition.get_classifier(
        #     classifier_id='elderlyFallPain_700377303')
        # print(json.dumps(classifier, indent=2))

        with open(fullname, 'rb') as images_file:
            classes = visual_recognition.classify(
                images_file,
                parameters=json.dumps({
                    'classifier_ids': ['elderlyFallPain_700377303', 'default'],
                    'threshold': 0.2
                }))
        result = json.dumps(classes, indent=2)
        print(result)
        value = classes['images'][0]['classifiers'][0]['classes'][0]['score']
        print(value)
        ##############################
        # value = classification_result['results'][0]['predictions'][0]['labels'][keyword]
        if value > 0.4:
            new_fullname = base_folder + alert_filename
            os.renames(fullname, new_fullname)
            fullname = new_fullname

        insert_image(user_id, camera_id, fullname)

        response = flask.Response(result)
        response.headers['Access-Control-Allow-Origin'] = '*'  # This is important for Mobile Device
        return response

@app.route('/rest/api/check', methods=['POST'])
def check():
    user_id = flask.session['email_address']
    camera_id = request.values['camera_id']
    image_path = get_image(user_id, camera_id)
    # if os.path.isfile(image_path):
    #     return image_path
    # else:
    #     image_path = 'static/monitor/' + user_id + '/' + camera_id + '/monitor.jpeg'
    #     if os.path.isfile(image_path):
    #         return image_path
    # return 'Error: no image found.'
    return image_path

@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():

    # Specify the state when creating the flow in the callback so that it can
    #  verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    user = flow.oauth2session.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
    flask.session['email_address'] = user['email']
    print(user)

    return flask.redirect(flask.url_for('hello'))

# user = User.filter_by(google_id=userinfo['id']).first()
#     if user:
#         user.name = userinfo['name']
#         user.avatar = userinfo['picture']
#     else:
#         user = User(google_id=userinfo['id'],
#                     name=userinfo['name'],
#                     avatar=userinfo['picture'])
#     db.session.add(user)
#     db.session.flush()
#     login_user(user)
#     return redirect(url_for('index'))


@app.route('/logout')
def logout():
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        clear_credentials()
        return flask.redirect(flask.url_for('hello'))
        # return('Credentials successfully revoked.' + print_index_table())
    else:
        return ('An error occurred.' + print_index_table())

@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return flask.redirect(flask.url_for('hello'))
    # return ('Credentials have been cleared.<br><br>' +
    #         print_index_table())

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')

#############################

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(host='0.0.0.0', port=80, threaded=True)
# # host='0.0.0.0', port='80',