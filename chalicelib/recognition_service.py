import boto3
from botocore.exceptions import ClientError
import logging


class RecognitionService:
    def __init__(self):
        try:
            self.client = boto3.client('rekognition')
        except Exception as e:
            error = e.__class__.__name__
            if error == "AccessDeniedException":
                logging.error(e)
                return "You are not authorized to use the service. Plase check logs for more details"
            else:
                logging.error(e)
                return "Something went wrong with connecting to AWS Rekognition. Please check logs for more details."

    def detect_text(self, file_bytes):
        try:
            response = self.client.detect_text(Image={'Bytes': file_bytes})
        except Exception as e:
            error_name = e.__class__.__name__
            if error_name == "ImageTooLargeException":
                logging.error(e)
                return "The provided image is too large. Kindly use smaller image."
            else:
                logging.log(e)
                return "Something went wrong with detecting text. Plase check logs for more details."
        lines = []
        for detection in response['TextDetections']:
            if detection['Type'] == 'LINE':
                try:
                    lines.append({
                        'text': detection['DetectedText'],
                        'confidence': detection['Confidence'],
                        'boundingBox': detection['Geometry']['BoundingBox']
                    })
                except ClientError as ce:
                    logging.error(ce)
                    return "Error in appending text detections"

        return lines
