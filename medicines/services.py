from .models import Medicine, Category

class SymptomSearchService:
    # Basic mapping of symptoms to categories/medicine keywords
    SYMPTOM_MAP = {
        "fever": ["fever", "paracetamol", "antipyretic"],
        "pain": ["analgesic", "pain relief", "aspirin"],
        "cough": ["cough", "syrup", "expectorant"],
        "cold": ["cold", "flu", "decongestant"],
        "தலைவலி": ["pain", "headache"], # Tamil voice search support
        "காய்ச்சல்": ["fever"],
    }

    @classmethod
    def find_medicines(cls, symptom_query):
        keywords = cls.SYMPTOM_MAP.get(symptom_query.lower(), [symptom_query])
        # Simple keyword-based AI search
        return Medicine.objects.filter(
            description__icontains=keywords[0]
        ) | Medicine.objects.filter(name__icontains=keywords[0])
