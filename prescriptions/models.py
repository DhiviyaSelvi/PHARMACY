from django.db import models
from django.conf import settings

class Prescription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    image = models.ImageField(upload_to='prescriptions/')

    # OCR results
    extracted_text = models.TextField(blank=True)
    is_validated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription by {self.user.username} on {self.created_at}"
