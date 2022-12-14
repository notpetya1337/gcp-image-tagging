import os
import re
import logging

logger = logging.getLogger(__name__)


def sanitize(s):
    n = "Empty"
    for i in s:
        n = i.replace("\t", "    ")
    return re.sub(r"[^ -~]", "", n)


class Tagging():
    def __init__(self, config):
        self.google_credentials = config.get('image-recognition', 'google-credentials')
        self.google_project = config.get('image-recognition', 'google-project')
        self.tags_backend = config.get('image-recognition', 'backend')

    def get_tags(self, image_binary):
        if self.tags_backend == 'google-vision':
            tags = self.google_vision_labels(image_binary=image_binary)
        elif self.tags_backend == 'aws-rekognition':
            tags = self.aws_rekognition(image_binary=image_binary)
        return tags

    def get_text(self, image_binary):
        if self.tags_backend == 'google-vision':
            text = self.google_vision_light_ocr(image_binary=image_binary)
        elif self.tags_backend == 'aws-rekognition':
            text = self.aws_rekognition(image_binary=image_binary)
        return text

    # TODO: this doesn't work yet
    def get_ocr_text(self, image_binary):
        if self.tags_backend == 'google-vision':
            ocrtext = self.google_vision_heavy_ocr(image_binary=image_binary)
        elif self.tags_backend == 'aws-rekognition':
            ocrtext = self.aws_rekognition(image_binary=image_binary)
        return ocrtext

    def google_vision_labels(self, image_binary):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.google_credentials
        os.environ["GOOGLE_CLOUD_PROJECT"] = self.google_project
        from google.cloud import vision
        client = vision.ImageAnnotatorClient()
        # Loads the image into memory
        image = vision.Image(content=image_binary)
        # image = client.annotate_image({'content': image_binary})
        # Performs label detection on the image file
        responsetags = client.label_detection(image=image)

        # TODO: make this work to save traffic on text recognition, maybe add face recognition
        # response = client.annotate_image({
        #     'image': {'source': {'image_uri': 'gs://my-test-bucket/image.jpg'}},
        #     'features': [
        #         {'type_': vision.Feature.Type.FACE_DETECTION},
        #         {"type_": vision_v1.Feature.Type.LABEL_DETECTION},]
        # })

        labels = responsetags.label_annotations
        tags = []
        for label in labels:
            tags.append(label.description)
        return tags

    def google_vision_light_ocr(self, image_binary):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.google_credentials
        os.environ["GOOGLE_CLOUD_PROJECT"] = self.google_project
        from google.cloud import vision
        client = vision.ImageAnnotatorClient()
        # Loads the image into memory
        image = vision.Image(content=image_binary)
        # image = client.annotate_image({'content': image_binary})
        # Performs label detection on the image file
        responsetags = client.text_detection(image=image)
        textobject = responsetags.text_annotations
        returntext = []
        for text in textobject:
            returntext.append(text.description)
        if not returntext:
            logger.info("Text not found in image, appending placeholder")
            returntext.append("No text detected.")
        return returntext

    # TODO: this doesn't work yet
    def google_vision_heavy_ocr(self, image_binary):

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.google_credentials
        os.environ["GOOGLE_CLOUD_PROJECT"] = self.google_project
        from google.cloud import vision
        client = vision.ImageAnnotatorClient()
        # Loads the image into memory
        image = vision.Image(content=image_binary)
        # image = client.annotate_image({'content': image_binary})
        # Performs label detection on the image file
        response = client.document_text_detection(image=image)
        textobject = response.text_annotations
        # returntext = []
        returntext = textobject
        # for text in textobject:
        #    returntext.append(text.description)
        # returntext = sanitize(returntext)
        return returntext

    def aws_rekognition(self, image_binary):
        return True
        # TODO add AWS support
