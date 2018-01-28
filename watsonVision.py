import json
from watson_developer_cloud import VisualRecognitionV3

# visual_recognition = VisualRecognitionV3(
#     '2016-05-20',
#     api_key='7e6e8982b7d6857732e15f7625c296035191d8d7'
# )

# Test a image with already trained classifier
# with open('C:/Users/kaich/Desktop/a.jpg', 'rb') as images_file:
#     classes = visual_recognition.classify(
#         images_file,
#         parameters=json.dumps({
#             'classifier_ids': ['elderlyFallPain_700377303','default'],
#             'threshold': 0.6
#         }))
# print(json.dumps(classes, indent=2))

# Creat a new classifier
# with open('./beagle.zip', 'rb') as beagle, open(
#         './golden-retriever.zip', 'rb') as goldenretriever, open(
#             './husky.zip', 'rb') as husky, open(
#                 './cats.zip', 'rb') as cats:
#     model = visual_recognition.create_classifier(
#         'dogs',
#         beagle_positive_examples=beagle,
#         goldenretriever_positive_examples=goldenretriever,
#         husky_positive_examples=husky,
#         negative_examples=cats)
# print(json.dumps(model, indent=2))

# Retrieve a list of custom classifiers
# classifiers = visual_recognition.list_classifiers(verbose=True)
# print(json.dumps(classifiers, indent=2))

# Update a classifier
# with open('./dalmatian.zip', 'rb') as dalmatian, open(
#         './more-cats.zip', 'rb') as more_cats:
#     updated_model = visual_recognition.update_classifier(
#         classifier_id='dogs_1477088859',
#         dalmatian_positive_examples=dalmatian,
#         negative_examples=more_cats)
# print(json.dumps(updated_model, indent=2))


# Delete a classifier
# response = visual_recognition.delete_classifier(classifier_id='dogs_1477088859')
# print(json.dumps(response, indent=2))

