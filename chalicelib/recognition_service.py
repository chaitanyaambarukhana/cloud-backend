import boto3
from botocore.exceptions import ClientError
import logging

class RecognitionService:
    def __init__(self):
        self.client = boto3.client('rekognition')

    def detect_text(self, file_bytes):
        try:
            response = self.client.detect_text(Image={'Bytes': file_bytes})
        except ClientError as ce:
            logging.error(ce)
            return "Error in detecting text"

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
