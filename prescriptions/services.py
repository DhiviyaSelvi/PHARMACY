import random
import time

class PrescriptionOCRService:
    @staticmethod
    def extract_medicines(image_path):
        """
        Mock OCR service that simulates extracting medicine names from an image.
        In production, this would use Google Vision API or Tesseract.
        """
        # Simulate processing time
        time.sleep(1)

        # Mock extracted data
        mock_results = [
            {"name": "Paracetamol 500mg", "dosage": "1-0-1", "duration": "5 days"},
            {"name": "Amoxicillin 250mg", "dosage": "1-1-1", "duration": "7 days"},
        ]

        return mock_results

    @staticmethod
    def validate_prescription(image_path):
        """
        Simulates AI validation of whether the image is a valid medical prescription.
        """
        # 90% chance to be valid in this mock
        return random.random() < 0.9
