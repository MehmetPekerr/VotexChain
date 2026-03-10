from Blockchain import Blockchain
from Observer import Observer
from Network import Node
import argparse
import sys
from datetime import datetime

def print_observers(chain):
    """Mevcut gözlemcileri listeler"""
    print("\nMevcut Gözlemciler:")
    for obs_id, observer in chain.observers.items():
        print(f"ID: {obs_id} - İsim: {observer.name}")

def main():
    # Komut satırı argümanlarını parse et
    parser = argparse.ArgumentParser(description='Blockchain Seçim Sistemi')
    parser.add_argument('--host', default='localhost', help='Node host adresi')
    parser.add_argument('--port', type=int, default=5000, help='Node port numarası')
    parser.add_argument('--peer', help='Bağlanılacak peer adresi (host:port)')
    args = parser.parse_args()

    try:
        # Node'u başlat
        node = Node(args.host, args.port)
        node.start()
        print(f"Node başlatıldı: {args.host}:{args.port}")

        # Blockchain'i başlat
        chain = Blockchain(node)
        
        # Örnek gözlemciler oluştur
        observer1 = Observer("OBS001", "Ahmet Yılmaz", "credentials1")
        observer2 = Observer("OBS002", "Mehmet Demir", "credentials2")
        
        # Gözlemcileri sisteme kaydet
        chain.register_observer(observer1)
        chain.register_observer(observer2)

        # Eğer peer belirtilmişse bağlan
        if args.peer:
            try:
                peer_host, peer_port = args.peer.split(':')
                peer_port = int(peer_port)
                if node.connect_to_peer(peer_host, peer_port):
                    print(f"Peer'a bağlanıldı: {peer_host}:{peer_port}")
                else:
                    print("Peer bağlantısı başarısız!")
            except Exception as e:
                print(f"Peer bağlantı hatası: {e}")

        print("Seçim Gözlem Sistemi'ne Hoş Geldiniz")
        print_observers(chain)  # Mevcut gözlemcileri göster
        
        current_observer = None  # Aktif gözlemci
        
        while True:
            if current_observer is None:
                # Giriş yapılmamışsa sadece giriş seçeneğini göster
                print("\nSeçenekler:")
                print("1- Gözlemci Girişi")
                print("0- Uygulamayı Kapat")
            else:
                # Giriş yapılmışsa tüm seçenekleri göster
                print(f"\nHoş geldiniz, {current_observer.name}")
                print("\nSeçenekler:")
                print("1- Çıkış Yap")
                print("2- Oy Takibi")
                print("3- Zinciri Görüntüle")
                print("4- Oy Sayımını Gör")
                print("5- Gözlemci Raporu Al")
                print("6- Zincir Bütünlüğünü Kontrol Et")
                print("7- Peer Listesini Göster")
                print("8- Yeni Peer'a Bağlan")
                print("9- Gözlemci Listesini Göster")
                print("0- Uygulamayı Kapat")

            try:
                secim = input("Seçiminizi Giriniz: ")
                
                if secim == "1":
                    if current_observer is None:
                        # Giriş yapılmamışsa giriş işlemi
                        observer_id = input("Gözlemci ID'nizi Giriniz: ")
                        if observer_id not in chain.observers:
                            print("Geçersiz gözlemci ID'si!")
                            print_observers(chain)
                            continue
                        current_observer = chain.observers[observer_id]
                        print(f"Hoş geldiniz, {current_observer.name}")
                    else:
                        # Giriş yapılmışsa çıkış işlemi
                        print(f"Çıkış yapılıyor... Hoşça kalın, {current_observer.name}")
                        current_observer = None
                    
                elif current_observer is not None:  # Sadece giriş yapılmışsa diğer seçenekleri göster
                    if secim == "2":
                        print("\nOy Takip Formu")
                        print("--------------")
                        sandik_no = input("Sandık No: ")
                        secmen_sayisi = input("Sandıktaki Toplam Seçmen Sayısı: ")
                        katilim_orani = input("Katılım Oranı (%): ")
                        
                        # Oy kullanım takibi
                        oy_kullananlar = []
                        while True:
                            secmen_id = input("\nSeçmen ID (Çıkmak için 'q'): ")
                            if secmen_id.lower() == 'q':
                                break
                                
                            if chain.has_voted(secmen_id):
                                print(f"UYARI: Bu seçmen daha önce oy kullanmış!")
                                continue
                                
                            oy_kullananlar.append(secmen_id)
                            print(f"Seçmen {secmen_id} oy kullanımı kaydedildi.")
                        
                        # Takip verilerini blockchain'e kaydet
                        takip_verisi = {
                            "sandik_no": sandik_no,
                            "secmen_sayisi": secmen_sayisi,
                            "katilim_orani": katilim_orani,
                            "oy_kullananlar": oy_kullananlar,
                            "gözlemci_id": current_observer.observer_id,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        try:
                            chain.add_transaction(takip_verisi, current_observer.observer_id)
                            print("\nOy takip verileri eklendi. Blok oluşturuluyor.....")
                            chain.mine_pending_transanction()
                            print("Oy takip verileri başarıyla kaydedildi ve doğrulandı.")
                        except ValueError as e:
                            print(f"Hata: {e}")
                            
                    elif secim == "3":
                        chain.print_chain()
                        
                    elif secim == "4":
                        print("\n----Oy Sayımı Yapılıyor...---")
                        results = chain.count_votes()
                        print("\nSandık Bazlı Katılım Oranları:")
                        for block in chain.chain:
                            for transaction in block.transactions:
                                if "sandik_no" in transaction:
                                    print(f"\nSandık No: {transaction['sandik_no']}")
                                    print(f"Toplam Seçmen: {transaction['secmen_sayisi']}")
                                    print(f"Katılım Oranı: {transaction['katilim_orani']}%")
                                    print(f"Oy Kullanan Seçmen Sayısı: {len(transaction['oy_kullananlar'])}")
                        
                    elif secim == "5":
                        try:
                            report = chain.get_observer_report(current_observer.observer_id)
                            print("\nGözlemci Raporu:")
                            print(f"Gözlemci: {report['name']}")
                            print(f"Toplam Takip Edilen Sandık: {report['total_verified_votes']}")
                            print("\nTakip Edilen Sandıklar:")
                            for vote in report['verified_votes']:
                                print(f"\nSandık No: {vote['sandik_no']}")
                                print(f"Toplam Seçmen: {vote['secmen_sayisi']}")
                                print(f"Katılım Oranı: {vote['katilim_orani']}%")
                                print(f"Oy Kullanan Seçmen Sayısı: {len(vote['oy_kullananlar'])}")
                                print(f"Zaman: {vote['timestamp']}")
                        except ValueError as e:
                            print(f"Hata: {e}")
                            
                    elif secim == "6":
                        print("\n--Zincir Kontrolü--")
                        if chain.is_chain_valid():
                            print("Zincir güvende")
                        else:
                            print("Zincir geçersiz! Veriler kurcalanmış olabilir")
                            
                    elif secim == "7":
                        print("\nBağlı Peer'lar:")
                        for peer in node.peers:
                            print(f"{peer['host']}:{peer['port']}")
                            
                    elif secim == "8":
                        peer_address = input("Peer adresini girin (host:port): ")
                        try:
                            peer_host, peer_port = peer_address.split(':')
                            peer_port = int(peer_port)
                            if node.connect_to_peer(peer_host, peer_port):
                                print(f"Peer'a bağlanıldı: {peer_host}:{peer_port}")
                            else:
                                print("Peer bağlantısı başarısız!")
                        except Exception as e:
                            print(f"Peer bağlantı hatası: {e}")
                            
                    elif secim == "9":
                        print_observers(chain)
                        
                elif secim == "0":
                    print("Uygulama kapatılıyor...")
                    node.stop()
                    break
                    
                else:
                    if current_observer is None:
                        print("Geçersiz seçim! Lütfen 1 veya 0 giriniz.")
                    else:
                        print("Geçersiz seçim! Lütfen 0-9 arasında bir değer giriniz.")
                    
            except KeyboardInterrupt:
                print("\nProgram kullanıcı tarafından durduruldu.")
                node.stop()
                break
            except Exception as e:
                print(f"Beklenmeyen bir hata oluştu: {e}")
                continue

    except Exception as e:
        print(f"Kritik hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()