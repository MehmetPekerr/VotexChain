import json
import hashlib
import time
import os
from typing import List, Dict, Optional, Any
from Network import Node
from datetime import datetime
from SmartContract import ElectionContract
from database import SessionLocal
from models import Block as DBBlock, Transaction
from sqlalchemy import desc, create_engine, Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class DBBlock(Base):
    __tablename__ = 'blocks'
    
    index = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    data = Column(JSON, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    hash = Column(String(64), nullable=False)
    nonce = Column(Integer, default=0)
    
    transactions = relationship("DBTransaction", back_populates="block")

class DBTransaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    block_id = Column(Integer, ForeignKey('blocks.index'))
    sender = Column(String(100), nullable=False)
    recipient = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    block = relationship("DBBlock", back_populates="transactions")

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.nonce = 0

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.transactions)}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }

    @classmethod
    def from_dict(cls, data: dict):
        block = cls(
            index=data["index"],
            transactions=data["transactions"],
            timestamp=data["timestamp"],
            previous_hash=data["previous_hash"]
        )
        block.nonce = data["nonce"]
        block.hash = data["hash"]
        return block

class Blockchain:
    def __init__(self, node: Optional[Node] = None):
        # Veritabanı bağlantısı
        self.engine = create_engine('postgresql://postgres:mpfb1907@localhost:5432/dagblockchain_db')
        self.create_tables()  # Tabloları oluştur
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        
        # Zinciri veritabanından yükle
        self.chain = self.load_chain_from_db()
        
        # Eğer zincir boşsa, genesis bloğunu oluştur
        if not self.chain:
            self.create_genesis_block()
        
        self.pending_transactions = []
        self.observers = {}
        self.node = node
        self.difficulty = 4  # Hash zorluğu
        self.mining_reward = 10  # Madencilik ödülü
        self.current_observer = None  # Aktif gözlemci
        self.smart_contract = ElectionContract()

    def create_tables(self):
        """Veritabanı tablolarını oluştur"""
        Base.metadata.create_all(self.engine)
        print("Veritabanı tabloları oluşturuldu.")

    def load_chain_from_db(self):
        """Zinciri veritabanından yükle"""
        blocks = self.db.query(DBBlock).order_by(DBBlock.index).all()
        return list(blocks)
    
    def create_genesis_block(self):
        """Genesis bloğunu oluştur"""
        genesis_block = DBBlock(
            index=0,
            timestamp=datetime.utcnow(),
            data=[],
            previous_hash="0" * 64,
            hash="0" * 64,
            nonce=0
        )
        self.db.add(genesis_block)
        self.db.commit()
        self.chain = [genesis_block]
    
    def get_latest_block(self):
        """Son bloğu getir"""
        return self.chain[-1]
    
    def calculate_hash(self, index, timestamp, data, previous_hash, nonce):
        """Blok hash'ini hesapla"""
        # Veriyi sıralı hale getir
        if isinstance(data, list):
            # Her bir işlemi sıralı hale getir
            sorted_data = []
            for transaction in data:
                if isinstance(transaction, dict):
                    # Sözlükleri sıralı hale getir
                    sorted_transaction = {}
                    for key in sorted(transaction.keys()):
                        if key != 'timestamp':  # timestamp'i hash hesaplamasından çıkar
                            sorted_transaction[key] = transaction[key]
                    sorted_data.append(sorted_transaction)
                else:
                    sorted_data.append(transaction)
            data = sorted_data
        
        # Hash hesaplama
        block_string = f"{index}{timestamp}{json.dumps(data, sort_keys=True)}{previous_hash}{nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def validate_chain(self):
        """Tüm zinciri doğrula"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Önceki hash kontrolü
            if current_block.previous_hash != previous_block.hash:
                return False
                
            # Hash doğrulama
            calculated_hash = self.calculate_hash(
                current_block.index,
                current_block.timestamp.isoformat(),
                current_block.data,
                current_block.previous_hash,
                current_block.nonce
            )
            
            if current_block.hash != calculated_hash:
                return False
                
            # Hash zorluğu kontrolü
            if not current_block.hash.startswith('0' * self.difficulty):
                return False
                
        return True

    def mine_pending_transanction(self):
        """Bekleyen işlemleri madencile"""
        if not self.pending_transactions:
            return

        previous_block = self.get_latest_block()
        new_index = previous_block.index + 1
        new_timestamp = datetime.utcnow()
        new_nonce = 0
        data = self.pending_transactions.copy()

        # Proof of Work
        while True:
            new_hash = self.calculate_hash(
                new_index,
                new_timestamp.isoformat(),
                data,
                previous_block.hash,
                new_nonce
            )
            if new_hash.startswith('0' * self.difficulty):
                break
            new_nonce += 1

        # Yeni blok oluştur
        new_block = DBBlock(
            index=new_index,
            timestamp=new_timestamp,
            data=data,
            previous_hash=previous_block.hash,
            hash=new_hash,
            nonce=new_nonce
        )

        # Veritabanına kaydet
        self.db.add(new_block)
        self.db.commit()

        # Zinciri güncelle
        self.chain = self.load_chain_from_db()
        self.pending_transactions = []

        # Zinciri doğrula
        if not self.validate_chain():
            raise Exception("Blockchain doğrulaması başarısız! Veritabanı bütünlüğü bozulmuş olabilir.")
    
    def add_transaction(self, sender, recipient, amount):
        """Yeni işlem ekle"""
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.pending_transactions.append(transaction)
    
    def get_balance(self, address):
        """Adres bakiyesini hesapla"""
        balance = 0
        
        for block in self.chain:
            for transaction in block.data:
                if transaction['sender'] == address:
                    balance -= transaction['amount']
                if transaction['recipient'] == address:
                    balance += transaction['amount']
        
        return balance

    def __del__(self):
        """Veritabanı bağlantısını kapat"""
        self.db.close()

    def register_observer(self, observer):
        """
        Yeni bir gözlemci kaydeder
        """
        self.observers[observer.observer_id] = observer
        return True

    def set_current_observer(self, observer):
        """
        Aktif gözlemciyi ayarlar
        """
        if observer and observer.observer_id in self.observers:
            if not self.current_observer:
                print("Aktif gözlemci bulunmuyor!")
                return False
            
            # Smart contract kurallarını kontrol et
            if not self.smart_contract.add_observer(observer.observer_id):
                print(f"Gözlemci {observer.observer_id} eklenemedi!")
                return False
            
            self.current_observer = observer
            return True
        return False

    def check_conflicting_info(self, new_transaction):
        """Aynı salon ve sandık için farklı gözlemcilerin girdiği bilgileri kontrol eder."""
        sandik_no = new_transaction.get("sandik_no")
        for block in self.chain:
            for transaction in block.data:
                if transaction.get("sandik_no") == sandik_no and transaction.get("gözlemci_id") != new_transaction.get("gözlemci_id"):
                    # Seçmen sayısı kontrolü
                    if "secmen_sayisi" in transaction and "secmen_sayisi" in new_transaction:
                        if transaction["secmen_sayisi"] != new_transaction["secmen_sayisi"]:
                            return f"Uyarı: {transaction['gözlemci_id']} ID'li gözlemci seçmen sayısını {transaction['secmen_sayisi']} olarak, siz ise {new_transaction['secmen_sayisi']} olarak girdiniz."
                    
                    # Katılan seçmen sayısı kontrolü
                    if "katilan_secmen" in transaction and "katilan_secmen" in new_transaction:
                        if transaction["katilan_secmen"] != new_transaction["katilan_secmen"]:
                            return f"Uyarı: {transaction['gözlemci_id']} ID'li gözlemci katılan seçmen sayısını {transaction['katilan_secmen']} olarak, siz ise {new_transaction['katilan_secmen']} olarak girdiniz."
                    
                    # Parti oyları kontrolü
                    if "party_votes" in transaction and "party_votes" in new_transaction:
                        for party, votes in transaction["party_votes"].items():
                            if party in new_transaction["party_votes"] and votes != new_transaction["party_votes"][party]:
                                return f"Uyarı: {transaction['gözlemci_id']} ID'li gözlemci {party} için {votes} oy sayısı girdi, siz ise {new_transaction['party_votes'][party]} girdiniz."
        
        return None

    def add_transaction(self, transaction: Dict[str, Any], observer_id: str) -> bool:
        if observer_id not in self.observers:
            raise ValueError("Geçersiz gözlemci ID'si")
            
        # İşlem formatını kontrol et
        if not isinstance(transaction, dict):
            raise ValueError("İşlem bir sözlük (dictionary) olmalıdır")
            
        # Gerekli alanların varlığını kontrol et
        required_fields = ["sandik_no"]
        if "secmen_sayisi" in transaction or "katilan_secmen" in transaction:
            required_fields.extend(["secmen_sayisi", "katilan_secmen", "oy_kullananlar"])
        
        for field in required_fields:
            if field not in transaction:
                raise ValueError(f"İşlemde {field} eksik")
        
        # Seçmen sayısı kontrolü
        if "secmen_sayisi" in transaction and "katilan_secmen" in transaction:
            if int(transaction["katilan_secmen"]) > int(transaction["secmen_sayisi"]):
                raise ValueError("Katılan seçmen sayısı toplam seçmen sayısından büyük olamaz!")
            
            # Katılım oranını hesapla
            transaction["katilim_orani"] = round((int(transaction["katilan_secmen"]) / int(transaction["secmen_sayisi"])) * 100, 2)
            
            # Oy kullananlar listesi kontrolü
            if not isinstance(transaction["oy_kullananlar"], list):
                raise ValueError("Oy kullananlar bir liste olmalı!")
                
            if len(transaction["oy_kullananlar"]) != int(transaction["katilan_secmen"]):
                raise ValueError("Oy kullanan seçmen sayısı ile katılan seçmen sayısı eşleşmiyor!")
            
        # Gözlemci ID'sini ekle
        transaction["gözlemci_id"] = observer_id
        
        # Zaman damgası ekle (eğer yoksa)
        if "timestamp" not in transaction:
            transaction["timestamp"] = datetime.now().isoformat()
        
        # Çelişkili bilgi kontrolü
        conflict_warning = self.check_conflicting_info(transaction)
        if conflict_warning:
            raise ValueError(conflict_warning)
            
        # Eğer node varsa, işlemi diğer düğümlere yayınla
        if self.node:
            self.node.broadcast_transaction(transaction)
        
        # İşlemi bekleyen işlemler listesine ekle
        self.pending_transactions.append(transaction)
        
        # Bekleyen işlemleri madenciliğe gönder
        if len(self.pending_transactions) >= 1:  # Her işlem için yeni blok oluştur
            self.mine_pending_transanction()
            
        return True
        
        # İşlemi geri al
        self.pending_transactions.pop()
        raise

    def print_chain(self):
        """Blockchain'i görüntüle"""
        chain_text = "Blockchain:\n\n"
        for block in self.chain:
            chain_text += f"Blok #{block.index}\n"
            chain_text += f"Hash: {block.hash}\n"
            chain_text += f"Önceki Hash: {block.previous_hash}\n"
            chain_text += f"Zaman: {block.timestamp}\n"
            chain_text += f"Nonce: {block.nonce}\n"
            chain_text += "İşlemler:\n"
            
            for transaction in block.data:
                if isinstance(transaction, dict):
                    chain_text += f"- Sandık No: {transaction.get('sandik_no', 'N/A')}\n"
                    chain_text += f"  Toplam Seçmen: {transaction.get('secmen_sayisi', 'N/A')}\n"
                    chain_text += f"  Katılan Seçmen: {transaction.get('katilan_secmen', 'N/A')}\n"
                    chain_text += f"  Katılım Oranı: {transaction.get('katilim_orani', 'N/A')}%\n"
                    
                    if "party_votes" in transaction:
                        chain_text += "  Parti Oyları:\n"
                        for party, votes in transaction["party_votes"].items():
                            chain_text += f"    {party}: {votes}\n"
                    
                    chain_text += f"  Oy Kullananlar: {', '.join(transaction.get('oy_kullananlar', []))}\n"
                    chain_text += f"  Gözlemci: {transaction.get('gözlemci_id', 'N/A')}\n"
                    chain_text += f"  Zaman: {transaction.get('timestamp', 'N/A')}\n"
                else:
                    chain_text += f"- {transaction}\n"
            chain_text += "\n"
        return chain_text

    def count_votes(self):
        """Tüm sandıklardaki oyları say"""
        results = {
            "sandiklar": {},
            "observer_stats": {observer_id: 0 for observer_id in self.observers},
            "toplam_secmen": 0,
            "toplam_katilim": 0,
            "parti_oylari": {}
        }
        
        for block in self.chain:
            for transaction in block.data:
                if isinstance(transaction, dict) and "sandik_no" in transaction:
                    sandik_no = transaction["sandik_no"]
                    observer_id = transaction["gözlemci_id"]
                    
                    # Sandık bilgilerini kaydet
                    if sandik_no not in results["sandiklar"]:
                        results["sandiklar"][sandik_no] = {
                            "secmen_sayisi": transaction.get("secmen_sayisi", 0),
                            "katilan_secmen": transaction.get("katilan_secmen", 0),
                            "katilim_orani": transaction.get("katilim_orani", 0),
                            "oy_kullananlar": transaction.get("oy_kullananlar", []),
                            "gözlemciler": set()
                        }
                    
                    # Gözlemci istatistiklerini güncelle
                    results["observer_stats"][observer_id] = results["observer_stats"].get(observer_id, 0) + 1
                    results["sandiklar"][sandik_no]["gözlemciler"].add(observer_id)
                    
                    # Parti oylarını topla
                    if "party_votes" in transaction:
                        for party, votes in transaction["party_votes"].items():
                            if party not in results["parti_oylari"]:
                                results["parti_oylari"][party] = 0
                            results["parti_oylari"][party] += votes
                    
                    # Toplam seçmen ve katılım sayılarını güncelle
                    results["toplam_secmen"] += transaction.get("secmen_sayisi", 0)
                    results["toplam_katilim"] += transaction.get("katilan_secmen", 0)
        
        # Genel katılım oranını hesapla
        if results["toplam_secmen"] > 0:
            results["genel_katilim_orani"] = round((results["toplam_katilim"] / results["toplam_secmen"]) * 100, 2)
        else:
            results["genel_katilim_orani"] = 0
            
        return results

    def compare_sandik_data(self, sandik_no):
        """Belirli bir sandık için tüm gözlemcilerin verilerini karşılaştır"""
        sandik_data = []
        
        for block in self.chain:
            for transaction in block.data:
                if isinstance(transaction, dict) and transaction.get("sandik_no") == sandik_no:
                    sandik_data.append({
                        "gözlemci_id": transaction.get("gözlemci_id"),
                        "secmen_sayisi": transaction.get("secmen_sayisi"),
                        "katilan_secmen": transaction.get("katilan_secmen"),
                        "katilim_orani": transaction.get("katilim_orani"),
                        "party_votes": transaction.get("party_votes", {}),
                        "oy_kullananlar": transaction.get("oy_kullananlar", []),
                        "timestamp": transaction.get("timestamp")
                    })
        
        if not sandik_data:
            return None, "Bu sandık için henüz kayıt yapılmamış."
            
        # Verileri karşılaştır
        comparison = {
            "sandik_no": sandik_no,
            "gözlemci_sayisi": len(sandik_data),
            "secmen_sayilari": {},
            "katilan_secmen_sayilari": {},
            "katilim_oranlari": {},
            "parti_oylari": {},
            "oy_kullananlar": {}
        }
        
        for data in sandik_data:
            observer_id = data["gözlemci_id"]
            comparison["secmen_sayilari"][observer_id] = data["secmen_sayisi"]
            comparison["katilan_secmen_sayilari"][observer_id] = data["katilan_secmen"]
            comparison["katilim_oranlari"][observer_id] = data["katilim_orani"]
            comparison["parti_oylari"][observer_id] = data["party_votes"]
            comparison["oy_kullananlar"][observer_id] = data["oy_kullananlar"]
        
        return comparison, None

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Hash kontrolü
            calculated_hash = self.calculate_hash(
                current_block.index,
                current_block.timestamp.isoformat(),
                current_block.data,
                current_block.previous_hash,
                current_block.nonce
            )
            if current_block.hash != calculated_hash:
                return False
                
            # Önceki hash kontrolü
            if current_block.previous_hash != previous_block.hash:
                return False
                
            # İşlem formatı kontrolü
            for transaction in current_block.data:
                if isinstance(transaction, dict):
                    required_fields = ["sandik_no", "secmen_sayisi", "katilan_secmen", "oy_kullananlar", "gözlemci_id"]
                    if not all(field in transaction for field in required_fields):
                        return False
                        
        return True

    def get_observer_report(self, observer_id):
        """
        Belirli bir gözlemcinin raporunu döndürür
        """
        if observer_id not in self.observers:
            raise ValueError("Geçersiz gözlemci ID'si")
        
        return self.observers[observer_id].get_verification_report()

    def replace_chain(self, new_chain: List[Block]):
        """
        Mevcut zinciri yeni zincirle değiştirir (eğer yeni zincir daha uzunsa)
        """
        if len(new_chain) <= len(self.chain):
            return False

        # Yeni zincirin geçerliliğini kontrol et
        temp_chain = [Block.from_dict(block) for block in new_chain]
        for i in range(1, len(temp_chain)):
            current = temp_chain[i]
            previous = temp_chain[i-1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
            if not current.hash.startswith('0' * self.difficulty):
                return False

        self.chain = temp_chain
        self.save_blockchain()
        return True
        
    def save_blockchain(self):
        try:
            # Geçici dosya kullanarak güvenli kaydetme
            temp_file = "blockchain_data.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump([block.to_dict() for block in self.chain], f, ensure_ascii=False, indent=2)
            
            # Eğer hedef dosya varsa önce sil
            if os.path.exists("blockchain_data.json"):
                os.remove("blockchain_data.json")
            
            # Geçici dosyayı asıl dosyaya taşı
            os.rename(temp_file, "blockchain_data.json")
            print("Blockchain verileri kaydedildi.")
        except Exception as e:
            print(f"Blockchain kaydedilirken hata oluştu: {str(e)}")
            # Geçici dosyayı temizle
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            raise  # Hatayı yukarı ilet

    def has_voted_anywhere(self, secmen_id):
        """
        Bir seçmenin herhangi bir sandıkta oy kullanıp kullanmadığını kontrol eder
        """
        for block in self.chain:
            for transaction in block.data:
                if isinstance(transaction, dict) and "oy_kullananlar" in transaction:
                    if secmen_id in transaction["oy_kullananlar"]:
                        return True
        return False

    def verify_chain_integrity(self):
        """
        Blockchain'in bütünlüğünü kontrol eder
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Önceki bloğun hash'ini kontrol et
            if current_block.previous_hash != previous_block.hash:
                return False, f"Blok {i} için önceki hash değeri uyuşmuyor"
            
            # Mevcut bloğun hash'ini kontrol et
            if current_block.hash != current_block.calculate_hash():
                return False, f"Blok {i} için hash değeri değiştirilmiş"
        
        return True, "Blockchain bütünlüğü doğrulandı"
        