import socket
import threading
import json
import time
from typing import List, Dict

class Node:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.peers: List[Dict] = []  # Bağlı node'lar
        self.server_socket = None
        self.is_running = False
        self._lock = threading.Lock()  # Thread güvenliği için kilit

    def start(self):
        """Node'u başlatır ve dinlemeye başlar"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.is_running = True

            # Dinleme thread'ini başlat
            listen_thread = threading.Thread(target=self._listen_for_connections)
            listen_thread.daemon = True  # Ana program kapandığında thread'in de kapanmasını sağlar
            listen_thread.start()
        except Exception as e:
            print(f"Node başlatma hatası: {e}")
            self.stop()
            raise

    def _listen_for_connections(self):
        """Gelen bağlantıları dinler"""
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.is_running:  # Sadece çalışır durumdayken hata mesajı göster
                    print(f"Bağlantı hatası: {e}")

    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """İstemci bağlantılarını yönetir"""
        try:
            while self.is_running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                message = json.loads(data.decode())
                self._process_message(message)
        except Exception as e:
            if self.is_running:
                print(f"İstemci işleme hatası: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass

    def _process_message(self, message: dict):
        """Gelen mesajları işler"""
        message_type = message.get('type')
        
        if message_type == 'new_block':
            # Yeni blok bilgisi
            self._handle_new_block(message['data'])
        elif message_type == 'new_transaction':
            # Yeni işlem bilgisi
            self._handle_new_transaction(message['data'])
        elif message_type == 'sync_request':
            # Zincir senkronizasyon isteği
            self._handle_sync_request(message['data'])
        elif message_type == 'peer_list':
            # Peer listesi güncelleme
            self._handle_peer_list(message['data'])

    def connect_to_peer(self, host: str, port: int):
        """Yeni bir peer'a bağlanır"""
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((host, port))
            
            with self._lock:
                # Peer bilgisini kaydet
                self.peers.append({
                    'host': host,
                    'port': port,
                    'socket': peer_socket
                })
            
            # Peer listesini iste
            self._request_peer_list(peer_socket)
            
            # Zincir senkronizasyonu iste
            self._request_chain_sync(peer_socket)
            
            return True
        except Exception as e:
            print(f"Peer bağlantı hatası: {e}")
            return False

    def broadcast_message(self, message: dict):
        """Mesajı tüm peer'lara yayınlar"""
        with self._lock:
            peers_to_remove = []
            for peer in self.peers:
                try:
                    peer['socket'].send(json.dumps(message).encode())
                except Exception as e:
                    print(f"Yayın hatası: {e}")
                    peers_to_remove.append(peer)
            
            # Bağlantısı kopmuş peer'ları listeden çıkar
            for peer in peers_to_remove:
                try:
                    peer['socket'].close()
                except:
                    pass
                self.peers.remove(peer)

    def _request_peer_list(self, peer_socket: socket.socket):
        """Peer listesini ister"""
        message = {
            'type': 'peer_list_request'
        }
        peer_socket.send(json.dumps(message).encode())

    def _request_chain_sync(self, peer_socket: socket.socket):
        """Zincir senkronizasyonu ister"""
        message = {
            'type': 'sync_request',
            'data': {
                'last_block_index': 0  # Tüm zinciri iste
            }
        }
        peer_socket.send(json.dumps(message).encode())

    def broadcast_transaction(self, transaction: dict):
        """Yeni bir işlemi tüm peer'lara yayınlar"""
        message = {
            'type': 'new_transaction',
            'data': transaction
        }
        self.broadcast_message(message)
    
    def stop(self):
        """Node'u durdurur"""
        self.is_running = False
        
        # Server socket'i kapat
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        # Peer bağlantılarını kapat
        with self._lock:
            for peer in self.peers:
                try:
                    peer['socket'].close()
                except:
                    pass
            self.peers.clear() 