class MockGeoCoder:
    # Sample mapping for major TN locations
    PINCODE_MAP = {
        "641002": (11.0011, 76.9467), # RS Puram, Coimbatore
        "600001": (13.0827, 80.2707), # Chennai Central
        "625001": (9.9252, 78.1198),  # Madurai
    }

    @classmethod
    def get_coordinates(cls, pincode):
        """
        Simulates geocoding external API.
        Returns (lat, lon) or None.
        """
        return cls.PINCODE_MAP.get(str(pincode))
