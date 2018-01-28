from flask import Flask, request


import json
from watson_developer_cloud import VisualRecognitionV3


app = Flask(__name__)


visual_recognition = VisualRecognitionV3(
    '2018-01-27',
    api_key='{api_key~~~~~~~ our api_key}')

classifier = visual_recognition.get_classifier(
    classifier_id='???????????????????')
print(json.dumps(classifier, indent=2))
# with open('./fruitbowl.jpg', 'rb') as images_file:
#     classes = visual_recognition.classify(
#         images_file,
#         parameters=json.dumps({
#             'classifier_ids': ['fruits_1462128776','SatelliteModel_6242312846'],
#             'threshold': 0.6
#         }))
# print(json.dumps(classes, indent=2))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)
# host='0.0.0.0', port='80',