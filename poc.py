from flask import Flask, request, redirect
from flask_jsonpify import jsonify
from pymongo import mongo_client
import flask
import requests


import os
import time
import json
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
            c_list.append({'camera_id': c['camera_id'], 'detector_id': c['detector_id'], 'detector_name': name})
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
    return redirect('http://localhost:5000/index.html', code=302)


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
        detector_id = ''
        fullname = ''
        # Classifying a picture from a file path
        print(detector_id, fullname)
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
        if value > 0.5:
            new_fullname = base_folder + alert_filename
            os.renames(fullname, new_fullname)
            fullname = new_fullname

        insert_image(user_id, camera_id, fullname)

        response = flask.Response(result)
        response.headers['Access-Control-Allow-Origin'] = '*'  # This is important for Mobile Device
        return response


#############################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
# # host='0.0.0.0', port='80',