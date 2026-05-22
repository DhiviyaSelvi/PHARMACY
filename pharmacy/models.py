from django.db import models

# All core models have been moved to modular apps:
# - Pharmacy -> pharmacies/models.py
# - Category, Medicine -> medicines/models.py
# - Cart, CartItem -> orders/models.py (or dedicated app)
# - Order, OrderItem -> orders/models.py
# - Prescription -> prescriptions/models.py

# This file is kept minimal to avoid breaking legacy imports
# during the transition, but models are being deprecated.
