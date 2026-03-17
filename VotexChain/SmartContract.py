from typing import Dict, List, Any
from datetime import datetime

class SmartContract:
    def __init__(self):
        self.state: Dict[str, Any] = {}
        self.rules = {}
        self.events = []
    
    def add_rule(self, rule_name: str, rule_function):
        """Yeni bir kural ekler"""
        self.rules[rule_name] = rule_function
    
    def get_state(self) -> Dict[str, Any]:
        """Mevcut durumu döndürür"""
        return self.state
    
    def update_state(self, key: str, value: Any):
        """Durum güncellemesi yapar"""
        self.state[key] = value
        self.events.append({
            'type': 'state_update',
            'key': key,
            'value': value,
            'timestamp': datetime.now().isoformat()
        })

class ElectionContract(SmartContract):
    def __init__(self, min_observers: int = 3):
        super().__init__()
        self.state.update({
            'is_active': False,
            'observers': set(),
            'min_observers': min_observers,
            'ballot_boxes': {},
            'voter_registry': set()
        })
        
        # Temel kuralları ekle
        self.add_rule('can_start_election', self._can_start_election)
        self.add_rule('can_vote', self._can_vote)
        self.add_rule('can_add_ballot_box', self._can_add_ballot_box)
        self.add_rule('can_add_observer', self._can_add_observer)
    
    def _can_start_election(self) -> bool:
        """Seçimin başlayıp başlayamayacağını kontrol eder"""
        return len(self.state['observers']) >= self.state['min_observers']
    
    def _can_vote(self, voter_id: str, ballot_box_id: str) -> bool:
        """Bir seçmenin oy kullanıp kullanamayacağını kontrol eder"""
        if not self.state['is_active']:
            return False
        if voter_id in self.state['voter_registry']:
            return False
        if ballot_box_id not in self.state['ballot_boxes']:
            return False
        return True
    
    def _can_add_ballot_box(self, ballot_box_id: str, observer_id: str) -> bool:
        """Yeni sandık eklenip eklenemeyeceğini kontrol eder"""
        if not self.state['is_active']:
            return False
        if observer_id not in self.state['observers']:
            return False
        if ballot_box_id in self.state['ballot_boxes']:
            return False
        return True
    
    def _can_add_observer(self, observer_id: str) -> bool:
        """Yeni gözlemci eklenip eklenemeyeceğini kontrol eder"""
        return observer_id not in self.state['observers']
    
    def start_election(self) -> bool:
        """Seçimi başlatır"""
        if self._can_start_election():
            self.update_state('is_active', True)
            return True
        return False
    
    def add_observer(self, observer_id: str) -> bool:
        """Yeni bir gözlemci ekler"""
        if self._can_add_observer(observer_id):
            observers = self.state['observers']
            observers.add(observer_id)
            self.update_state('observers', observers)
            return True
        return False
    
    def register_voter(self, voter_id: str) -> bool:
        """Yeni bir seçmen kaydeder"""
        if voter_id in self.state['voter_registry']:
            return False
        voters = self.state['voter_registry']
        voters.add(voter_id)
        self.update_state('voter_registry', voters)
        return True
    
    def validate_vote(self, voter_id: str, ballot_box_no: str) -> bool:
        """Seçmenin oy kullanma hakkını doğrular"""
        if voter_id not in self.state['voter_registry']:
            return False
        if ballot_box_no not in self.state['ballot_boxes']:
            return False
        return True
    
    def validate_ballot_box(self, ballot_box_no: str, total_voters: int, participating_voters: int) -> bool:
        """Sandık bilgilerinin doğruluğunu kontrol eder"""
        if participating_voters > total_voters:
            return False
        return True
    
    def validate_party_votes(self, ballot_box_no: str, party_votes: dict, total_votes: int) -> bool:
        """Parti oylarının doğruluğunu kontrol eder"""
        if sum(party_votes.values()) != total_votes:
            return False
        return True
    
    def register_ballot_box(self, ballot_box_no: str, total_voters: int) -> bool:
        """Yeni bir sandık kaydeder"""
        if ballot_box_no in self.state['ballot_boxes']:
            return False
        ballot_boxes = self.state['ballot_boxes']
        ballot_boxes[ballot_box_no] = {
            "total_voters": total_voters,
            "participating_voters": 0,
            "party_votes": {}
        }
        self.update_state('ballot_boxes', ballot_boxes)
        return True
    
    def get_results(self) -> Dict[str, Any]:
        """Seçim sonuçlarını döndürür"""
        return {
            'total_voters': len(self.state['voter_registry']),
            'total_ballot_boxes': len(self.state['ballot_boxes']),
            'ballot_boxes': self.state['ballot_boxes'],
            'is_active': self.state['is_active']
        }
