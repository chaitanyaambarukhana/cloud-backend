import boto3


class RecognitionService:
    def __init__(self):
        self.client = boto3.client('rekognition')

    def detect_text(self, file_bytes):
        response = self.client.detect_text(
            Image={
                'Bytes': file_bytes
            }
        )

        lines = []
        for detection in response['TextDetections']:
            if detection['Type'] == 'LINE':
                lines.append({
                    'text': detection['DetectedText'],
                    'confidence': detection['Confidence'],
                    'boundingBox': detection['Geometry']['BoundingBox']
                })

        return lines
