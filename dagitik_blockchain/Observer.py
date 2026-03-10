import hashlib
import json
from datetime import datetime

class Observer:
    def __init__(self, observer_id, name, credentials):
        self.observer_id = observer_id
        self.name = name
        self.credentials = credentials
        self.verified_votes = []
    
    def verify_vote(self, vote_data):
        """
        Oy takip verilerini doğrular ve imzalar
        """
        verification_data = {
            "sandik_no": vote_data["sandik_no"],
            "secmen_sayisi": vote_data["secmen_sayisi"],
            "katilim_orani": vote_data["katilim_orani"],
            "oy_kullananlar": vote_data["oy_kullananlar"],
            "gözlemci_id": self.observer_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # İmza oluştur
        signature = self._create_signature(verification_data)
        verification_data["signature"] = signature
        
        self.verified_votes.append(verification_data)
        return verification_data
    
    def _create_signature(self, data):
        """
        Veri için benzersiz imza oluşturur
        """
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def get_verification_report(self):
        """
        Gözlemcinin doğruladığı oy takip verilerinin raporunu döndürür
        """
        return {
            "observer_id": self.observer_id,
            "name": self.name,
            "total_verified_votes": len(self.verified_votes),
            "verified_votes": self.verified_votes
        } 