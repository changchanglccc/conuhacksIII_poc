import json
from watson_developer_cloud import VisualRecognitionV3

visual_recognition = VisualRecognitionV3(
    '2016-05-20',
    api_key='{api_key}')

with open('./fruitbowl.jpg', 'rb') as images_file:
    classes = visual_recognition.classify(
        images_file,
        parameters=json.dumps({
            'classifier_ids': ['fruits_1462128776','SatelliteModel_6242312846'],
            'threshold': 0.6
        }))
print(json.dumps(classes, indent=2))