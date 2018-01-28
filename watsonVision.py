import json
from watson_developer_cloud import VisualRecognitionV3

visual_recognition = VisualRecognitionV3(
    '2016-05-20',
    api_key='7e6e8982b7d6857732e15f7625c296035191d8d7'
)


with open('C:/Users/kaich/Desktop/a.jpg', 'rb') as images_file:
    classes = visual_recognition.classify(
        images_file,
        parameters=json.dumps({
            'classifier_ids': ['elderlyFallPain_700377303','default'],
            'threshold': 0.6
        }))
print(json.dumps(classes, indent=2))

