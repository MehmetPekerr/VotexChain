import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from Blockchain import Blockchain
from Observer import Observer
from Network import Node
import threading
from datetime import datetime
import requests

class SeçimGözlemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Seçim Gözlem Sistemi")
        self.root.geometry("800x600")
        
        # Node ve Blockchain başlatma
        self.node = Node("localhost", 5000)
        self.node.start()
        self.chain = Blockchain(self.node)
        
        # Örnek gözlemciler
        observer1 = Observer("OBS001", "Ahmet Yılmaz", "credentials1")
        observer2 = Observer("OBS002", "Mehmet Demir", "credentials2")
        self.chain.register_observer(observer1)
        self.chain.register_observer(observer2)
        
        self.current_observer = None
        self.current_salon = None
        self.current_sandik = None
        self.current_total_voters = 0  # Toplam seçmen sayısı
        self.voter_count = 0  # Seçmen sayısı sayaçı
        self.setup_gui()
        
    def setup_gui(self):
        # Ana frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Giriş frame'i
        self.login_frame = ttk.LabelFrame(self.main_frame, text="Gözlemci Girişi", padding="10")
        self.login_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.login_frame, text="Gözlemci ID:").grid(row=0, column=0, padx=5)
        self.observer_id_entry = ttk.Entry(self.login_frame)
        self.observer_id_entry.grid(row=0, column=1, padx=5)
        
        ttk.Button(self.login_frame, text="Giriş Yap", command=self.login).grid(row=0, column=2, padx=5)
        ttk.Button(self.login_frame, text="Gözlemci Listesi", command=self.show_observers).grid(row=0, column=3, padx=5)
        ttk.Button(self.login_frame, text="Çıkış Yap", command=self.logout).grid(row=0, column=4, padx=5)
        
        # Konum seçim frame'i
        self.location_frame = ttk.LabelFrame(self.main_frame, text="Konum Seçimi", padding="10")
        self.location_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.location_frame, text="Salon No:").grid(row=0, column=0, padx=5)
        self.location_salon_no_entry = ttk.Entry(self.location_frame)
        self.location_salon_no_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.location_frame, text="Sandık No:").grid(row=1, column=0, padx=5)
        self.location_sandik_no_entry = ttk.Entry(self.location_frame)
        self.location_sandik_no_entry.grid(row=1, column=1, padx=5)
        
        ttk.Label(self.location_frame, text="Toplam Seçmen Sayısı:").grid(row=2, column=0, padx=5)
        self.location_total_voters_entry = ttk.Entry(self.location_frame)
        self.location_total_voters_entry.grid(row=2, column=1, padx=5)
        
        ttk.Button(self.location_frame, text="Devam Et", command=self.show_location).grid(row=3, column=0, columnspan=2, pady=10)
        
        # İşlem seçim frame'i
        self.selection_frame = ttk.LabelFrame(self.main_frame, text="İşlem Seçimi", padding="10")
        self.selection_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Bilgi etiketi frame'i
        info_frame = ttk.Frame(self.selection_frame)
        info_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(info_frame, text="Salon No:").grid(row=0, column=0, padx=5)
        self.selection_salon_label = ttk.Label(info_frame, text="-")
        self.selection_salon_label.grid(row=0, column=1, padx=5)
        
        ttk.Label(info_frame, text="Sandık No:").grid(row=0, column=2, padx=5)
        self.selection_sandik_label = ttk.Label(info_frame, text="-")
        self.selection_sandik_label.grid(row=0, column=3, padx=5)
        
        ttk.Label(info_frame, text="Toplam Seçmen:").grid(row=0, column=4, padx=5)
        self.selection_total_voters_label = ttk.Label(info_frame, text="-")
        self.selection_total_voters_label.grid(row=0, column=5, padx=5)
        
        # Butonlar
        button_frame = ttk.Frame(self.selection_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="← Geri", command=self.edit_location).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Oy Takibi", command=self.show_vote_tracking).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Parti Oyları", command=self.show_party_votes).grid(row=0, column=2, padx=5)
        
        # Rapor butonları
        report_frame = ttk.LabelFrame(self.selection_frame, text="Raporlar", padding="10")
        report_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(report_frame, text="Zinciri Görüntüle", command=self.show_chain).grid(row=0, column=0, padx=5, pady=2)
        ttk.Button(report_frame, text="Oy Sayımı", command=self.show_report).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(report_frame, text="Sandık Sandık Oy Sayımı", command=self.show_ballot_box_details).grid(row=0, column=2, padx=5, pady=2)
        ttk.Button(report_frame, text="Çakışmaları Kontrol Et", command=self.check_conflicts).grid(row=1, column=0, padx=5, pady=2)
        ttk.Button(report_frame, text="Zincir Kontrolü", command=self.check_chain).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(report_frame, text="Seçilen Sandık Karşılaştırması", command=self.compare_selected_ballot).grid(row=1, column=2, padx=5, pady=2)
        
        # Ana işlemler frame'i
        self.operations_frame = ttk.LabelFrame(self.main_frame, text="İşlemler", padding="10")
        self.operations_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Oy takip frame'i
        self.vote_tracking_frame = ttk.LabelFrame(self.operations_frame, text="Oy Takibi", padding="10")
        self.vote_tracking_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Geri dönüş butonu
        ttk.Button(self.vote_tracking_frame, text="← Geri", command=self.back_to_location).grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.vote_salon_label = ttk.Label(self.vote_tracking_frame, text="Salon No: ")
        self.vote_salon_label.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.vote_tracking_frame, text="Toplam Seçmen:").grid(row=0, column=2, padx=5)
        self.vote_total_voters_label = ttk.Label(self.vote_tracking_frame, text="-")
        self.vote_total_voters_label.grid(row=0, column=3, padx=5)
        
        ttk.Label(self.vote_tracking_frame, text="Sandık No:").grid(row=1, column=0, padx=5)
        self.sandik_no_entry = ttk.Entry(self.vote_tracking_frame)
        self.sandik_no_entry.grid(row=1, column=1, padx=5)
        
        # Seçmen ekleme alanı
        ttk.Label(self.vote_tracking_frame, text="Seçmen ID:").grid(row=2, column=0, padx=5)
        self.voter_id_entry = ttk.Entry(self.vote_tracking_frame)
        self.voter_id_entry.grid(row=2, column=1, padx=5)
        ttk.Button(self.vote_tracking_frame, text="Seçmen Ekle", command=self.add_voter).grid(row=2, column=2, padx=5)
        
        # Eklenen seçmen sayısı
        ttk.Label(self.vote_tracking_frame, text="Eklenen Seçmen:").grid(row=3, column=0, padx=5)
        self.voter_count_label = ttk.Label(self.vote_tracking_frame, text="0")
        self.voter_count_label.grid(row=3, column=1, padx=5)
        
        # Oy kullananlar listesi
        ttk.Label(self.vote_tracking_frame, text="Oy Kullananlar: (Seçmeni silmek için sağ tıklayın)").grid(row=4, column=0, columnspan=2, pady=5)
        self.oy_kullananlar_list = scrolledtext.ScrolledText(self.vote_tracking_frame, width=40, height=10)
        self.oy_kullananlar_list.grid(row=5, column=0, columnspan=3, pady=5)
        self.oy_kullananlar_list.bind('<Button-3>', self.remove_voter)
        self.oy_kullananlar_list.bind('<Key>', lambda e: "break")
        
        self.save_tracking_button = ttk.Button(self.vote_tracking_frame, text="Kaydet", command=self.save_vote_tracking, state='disabled')
        self.save_tracking_button.grid(row=7, column=1, padx=5)
        
        # Karşılaştırma butonu
        ttk.Button(self.vote_tracking_frame, text="Seçilen Sandık Karşılaştırması", command=self.compare_selected_ballot).grid(row=7, column=2, padx=5)
        
        # Parti oyları frame'i
        self.party_votes_frame = ttk.LabelFrame(self.operations_frame, text="Parti Oyları", padding="10")
        self.party_votes_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Geri dönüş butonu
        ttk.Button(self.party_votes_frame, text="← Geri", command=self.show_location).grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.party_salon_label = ttk.Label(self.party_votes_frame, text="Salon No: ")
        self.party_salon_label.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.party_votes_frame, text="Toplam Seçmen:").grid(row=0, column=2, padx=5)
        self.party_total_voters_label = ttk.Label(self.party_votes_frame, text="-")
        self.party_total_voters_label.grid(row=0, column=3, padx=5)
        
        ttk.Label(self.party_votes_frame, text="Sandık No:").grid(row=1, column=0, padx=5)
        self.party_sandik_no_entry = ttk.Entry(self.party_votes_frame)
        self.party_sandik_no_entry.grid(row=1, column=1, padx=5)
        
        # Parti listesi için frame
        self.party_list_frame = ttk.Frame(self.party_votes_frame)
        self.party_list_frame.grid(row=2, column=0, columnspan=4, pady=5)
        
        # Toplam oy sayısı
        ttk.Label(self.party_votes_frame, text="Toplam Oy:").grid(row=3, column=0, padx=5)
        self.total_votes_label = ttk.Label(self.party_votes_frame, text="0")
        self.total_votes_label.grid(row=3, column=1, padx=5)
        
        # Kaydet butonu
        ttk.Button(self.party_votes_frame, text="Kaydet", command=self.save_party_votes).grid(row=4, column=1, pady=10)
        
        # Karşılaştırma butonu
        ttk.Button(self.party_votes_frame, text="Seçilen Sandık Karşılaştırması", command=self.compare_selected_ballot).grid(row=4, column=2, pady=10)
        
        # Sabit partiler
        self.default_parties = ["A", "B", "C", "GEÇERSİZ"]
        
        # Parti oyları için değişkenler
        self.party_votes = {}
        self.party_vote_labels = {}
        
        # Rapor frame'i
        self.report_frame = ttk.LabelFrame(self.operations_frame, text="Raporlar", padding="10")
        self.report_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(self.report_frame, text="Zinciri Görüntüle", command=self.show_chain).grid(row=0, column=0, padx=5)
        ttk.Button(self.report_frame, text="Oy Sayımı", command=self.show_report).grid(row=1, column=0, padx=5)
        ttk.Button(self.report_frame, text="Zincir Kontrolü", command=self.check_chain).grid(row=2, column=0, padx=5)
        ttk.Button(self.report_frame, text="Çakışmaları Kontrol Et", command=self.check_conflicts).grid(row=3, column=0, padx=5)
        ttk.Button(self.report_frame, text="Sandık Sandık Oy Sayımı", command=self.show_ballot_box_details).grid(row=4, column=0, padx=5)
        
        # Log frame'i
        self.log_frame = ttk.LabelFrame(self.main_frame, text="Sistem Logları", padding="10")
        self.log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=10)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Başlangıçta işlem frame'lerini gizle
        self.location_frame.grid_remove()
        self.selection_frame.grid_remove()
        self.operations_frame.grid_remove()
        
    def log(self, message):
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        
    def login(self):
        observer_id = self.observer_id_entry.get()
        if observer_id in self.chain.observers:
            self.current_observer = self.chain.observers[observer_id]
            self.chain.set_current_observer(self.current_observer)
            self.location_frame.grid()
            self.log(f"Gözlemci girişi yapıldı: {self.current_observer.name}")
            messagebox.showinfo("Başarılı", f"Hoş geldiniz, {self.current_observer.name}")
        else:
            messagebox.showerror("Hata", "Geçersiz gözlemci ID'si!")
            
    def show_observers(self):
        observers_text = "Mevcut Gözlemciler:\n"
        for obs_id, observer in self.chain.observers.items():
            observers_text += f"ID: {obs_id} - İsim: {observer.name}\n"
        messagebox.showinfo("Gözlemciler", observers_text)
        
    def show_location(self):
        """Salon ve sandık bilgilerini al"""
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
            
        # Salon ve sandık bilgilerini al
        salon_no = self.location_salon_no_entry.get().strip()
        sandik_no = self.location_sandik_no_entry.get().strip()
        total_voters = self.location_total_voters_entry.get().strip()
        
        if not salon_no or not sandik_no or not total_voters:
            messagebox.showerror("Hata", "Lütfen salon, sandık numarası ve toplam seçmen sayısını girin!")
            return
            
        try:
            salon_no = int(salon_no)
            sandik_no = int(sandik_no)
            total_voters = int(total_voters)
            if total_voters <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hata", "Salon, sandık numarası ve toplam seçmen sayısı geçerli bir sayı olmalıdır!")
            return
            
        # Bilgileri kaydet
        self.current_salon = salon_no
        self.current_sandik = sandik_no
        self.current_total_voters = total_voters
        
        # İşlem seçim ekranını göster
        self.selection_frame.grid()
        self.location_frame.grid_remove()
        
        # İşlem frame'lerini gizle
        self.operations_frame.grid_remove()
        self.vote_tracking_frame.grid_remove()
        self.party_votes_frame.grid_remove()
        
        # İşlem ekranındaki bilgileri güncelle
        self.selection_salon_label.configure(text=salon_no)
        self.selection_sandik_label.configure(text=sandik_no)
        self.selection_total_voters_label.configure(text=str(total_voters))
        
        # Seçmen sayısını güncelle
        self.voter_count = 0
        self.voter_count_label.config(text="0")
        
        self.log(f"Salon {salon_no}, Sandık {sandik_no} seçildi (Toplam Seçmen: {total_voters})")
        
    def show_vote_tracking(self):
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
            
        # İşlem ekranını göster
        self.operations_frame.grid()
        self.selection_frame.grid_remove()
        
        # Salon, sandık ve seçmen bilgilerini güncelle
        self.vote_salon_label.configure(text=f"Salon No: {self.current_salon}")
        self.vote_total_voters_label.configure(text=str(self.current_total_voters))
        self.sandik_no_entry.delete(0, tk.END)
        self.sandik_no_entry.insert(0, self.current_sandik)
        self.sandik_no_entry.configure(state='readonly')
        
        # Blockchain'den en son kayıtlı seçmenleri yükle
        self.oy_kullananlar_list.delete("1.0", tk.END)
        latest_transaction = None
        latest_timestamp = None
        
        for block in self.chain.chain:
            for transaction in block.transactions:
                if isinstance(transaction, dict) and "sandik_no" in transaction:
                    if transaction["sandik_no"] == self.current_sandik and transaction["salon_no"] == self.current_salon:
                        if "oy_kullananlar" in transaction and "timestamp" in transaction:
                            # En son kaydı bul
                            current_timestamp = datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
                            if latest_timestamp is None or current_timestamp > latest_timestamp:
                                latest_timestamp = current_timestamp
                                latest_transaction = transaction
        
        # En son kaydı yükle
        if latest_transaction:
            for voter in latest_transaction["oy_kullananlar"]:
                if self.oy_kullananlar_list.get("1.0", tk.END).strip():
                    self.oy_kullananlar_list.insert(tk.END, f"\n{voter}")
                else:
                    self.oy_kullananlar_list.insert(tk.END, voter)
        
        # Seçmen sayısını güncelle
        self.update_voter_count()
        
        # Diğer frame'leri gizle
        self.party_votes_frame.grid_remove()
        
        # Oy takip frame'ini göster
        self.vote_tracking_frame.grid()
        
        # Seçmen sayısını güncelle
        self.update_voter_count()
        
        # Kaydet butonunu aktif yap
        if self.voter_count > 0:
            self.save_tracking_button.configure(state='normal')
        
        self.log(f"Salon {self.current_salon}, Sandık {self.current_sandik} için oy takibi işlemleri başlatıldı")
        
    def update_voter_count(self):
        # Seçmen listesindeki seçmen sayısını hesapla
        voters = self.oy_kullananlar_list.get("1.0", tk.END).strip().split('\n')
        self.voter_count = len([v for v in voters if v])
        self.voter_count_label.config(text=f"Eklenen Seçmen: {self.voter_count}")
        
        # Seçmen sayısına göre kaydet butonunu güncelle
        if self.voter_count > 0:
            self.save_tracking_button.configure(state='normal')
        else:
            self.save_tracking_button.configure(state='disabled')
            
    def remove_voter(self, event):
        try:
            # Tıklanan satırı bul
            index = self.oy_kullananlar_list.index(f"@{event.x},{event.y}")
            line_start = index.split('.')[0]
            line_end = self.oy_kullananlar_list.index(f"{line_start}.end")
            
            # Seçmen ID'sini al
            secmen_id = self.oy_kullananlar_list.get(f"{line_start}.0", line_end).strip()
            
            if secmen_id:
                # Silme işlemini onayla
                if messagebox.askyesno("Onayla", f"{secmen_id} ID'li seçmeni silmek istediğinize emin misiniz?"):
                    # Satırı sil
                    self.oy_kullananlar_list.delete(f"{line_start}.0", f"{int(line_start)+1}.0")
                    self.update_voter_count()
                    self.log(f"Seçmen silindi: {secmen_id}")
        except Exception as e:
            pass  # Tıklama boş alana yapıldıysa veya başka bir hata olduysa sessizce devam et
        
    def show_party_votes(self):
        # İşlem ekranını göster
        self.operations_frame.grid()
        self.selection_frame.grid_remove()
        
        # Son ekranı kaydet
        self.last_screen = 'party_votes'
        
        # Katılan seçmen sayısını al
        oy_kullananlar = self.oy_kullananlar_list.get("1.0", tk.END).strip().split("\n")
        katilan_secmen = len([x for x in oy_kullananlar if x])
        
        # Salon, sandık ve seçmen bilgilerini güncelle
        self.party_salon_label.configure(text=f"Salon No: {self.current_salon}")
        self.party_sandik_no_entry.delete(0, tk.END)
        self.party_sandik_no_entry.insert(0, self.current_sandik)
        self.party_sandik_no_entry.configure(state='readonly')
        self.party_total_voters_label.configure(text=f"Katılan Seçmen: {katilan_secmen}")
        
        # Diğer frame'leri gizle
        self.vote_tracking_frame.grid_remove()
        
        # Parti oyları frame'ini göster
        self.party_votes_frame.grid()
        
        # Rapor frame'ini göster
        self.report_frame.grid()
        
        # Eğer parti listesi boşsa, sabit partileri ekle
        if not self.party_votes:
            # Parti listesini temizle
            for widget in self.party_list_frame.winfo_children():
                widget.destroy()
            
            self.party_votes = {}
            self.party_vote_labels = {}
            self.total_votes_label.configure(text="0")
            
            # Sabit partileri ekle
            for party_name in self.default_parties:
                self.add_party_row(party_name)
        
        # Blockchain'den en son kayıtlı parti oylarını yükle
        latest_transaction = None
        latest_timestamp = None
        
        for block in self.chain.chain:
            for transaction in block.transactions:
                if isinstance(transaction, dict) and "sandik_no" in transaction:
                    if transaction["sandik_no"] == self.current_sandik and transaction["salon_no"] == self.current_salon:
                        if "party_votes" in transaction and "timestamp" in transaction:
                            # En son kaydı bul
                            current_timestamp = datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
                            if latest_timestamp is None or current_timestamp > latest_timestamp:
                                latest_timestamp = current_timestamp
                                latest_transaction = transaction
        
        # En son kaydı yükle
        if latest_transaction and "party_votes" in latest_transaction:
            for party, votes in latest_transaction["party_votes"].items():
                if party in self.party_votes:
                    self.party_votes[party] = votes
                    self.party_vote_labels[party].configure(text=str(votes))
            
            # Toplam oy sayısını güncelle
            total_votes = sum(self.party_votes.values())
            self.total_votes_label.configure(text=str(total_votes))
        
        self.log(f"Salon {self.current_salon}, Sandık {self.current_sandik} için parti oyları işlemleri başlatıldı")
        
    def add_voter(self):
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
            
        secmen_id = self.voter_id_entry.get().strip()
        if not secmen_id:
            messagebox.showerror("Hata", "Lütfen seçmen ID girin!")
            return
        
        # Global oy kullanım kontrolü
        if self.chain.has_voted_anywhere(secmen_id):
            messagebox.showerror("Hata", 
                f"Bu seçmen ID'si ({secmen_id}) herhangi bir sandıkta daha önce oy kullanmış!\n"
                "Aynı seçmen farklı sandıklara eklenemez!")
            return
        
        # Mevcut sandık kontrolü
        for block in self.chain.chain:
            for transaction in block.transactions:
                if isinstance(transaction, dict) and "oy_kullananlar" in transaction:
                    if secmen_id in transaction["oy_kullananlar"]:
                        if transaction.get("sandik_no") != self.current_sandik:
                            messagebox.showerror("Hata", 
                                f"Bu seçmen ID'si ({secmen_id}) farklı bir sandıkta kayıtlı!\n"
                                f"Sandık No: {transaction.get('sandik_no', 'Bilinmiyor')}\n"
                                f"Gözlemci: {transaction.get('gözlemci_id', 'Bilinmiyor')}\n"
                                f"Zaman: {transaction.get('timestamp', 'Bilinmiyor')}\n\n"
                                "Aynı seçmen farklı sandıklara eklenemez!")
                            return
                        elif transaction.get("gözlemci_id") == self.current_observer.observer_id:
                            messagebox.showerror("Hata", 
                                f"Bu seçmen ID'si ({secmen_id}) siz tarafından daha önce eklenmiş!\n"
                                f"Zaman: {transaction.get('timestamp', 'Bilinmiyor')}\n\n"
                                "Aynı seçmeni tekrar ekleyemezsiniz!")
                            return
        
        self.oy_kullananlar_list.insert(tk.END, f"{secmen_id}\n")
        self.voter_id_entry.delete(0, tk.END)
        self.update_voter_count()
        self.save_tracking_button.configure(state='normal')
        self.log(f"Seçmen eklendi: {secmen_id}")
        
    def save_vote_tracking(self):
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
            
        # Seçmen listesi boşsa uyarı ver
        current_voters = self.oy_kullananlar_list.get("1.0", tk.END).strip().split("\n")
        current_voters = [x for x in current_voters if x]
        
        if not current_voters:
            messagebox.showwarning("Uyarı", "Lütfen önce seçmen ekleyiniz!")
            return
            
        try:
            # Sandık numarasını al
            sandik_no = self.sandik_no_entry.get()
            if not sandik_no:
                messagebox.showerror("Hata", "Lütfen sandık numarasını girin!")
                return
                
            # Oy kullanan seçmenleri al
            oy_kullananlar = self.oy_kullananlar_list.get("1.0", tk.END).strip().split("\n")
            oy_kullananlar = [x for x in oy_kullananlar if x]
            katilan_secmen = len(oy_kullananlar)
            
            # Blockchain'deki son kaydı kontrol et
            latest_transaction = None
            latest_timestamp = None
            
            for block in self.chain.chain:
                for transaction in block.transactions:
                    if isinstance(transaction, dict) and "sandik_no" in transaction:
                        if transaction["sandik_no"] == sandik_no and transaction["salon_no"] == self.current_salon:
                            if "timestamp" in transaction:
                                current_timestamp = datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
                                if latest_timestamp is None or current_timestamp > latest_timestamp:
                                    latest_timestamp = current_timestamp
                                    latest_transaction = transaction
            
            # Eğer önceki kayıt varsa ve toplam seçmen sayısı farklıysa uyarı ver
            if latest_transaction and "secmen_sayisi" in latest_transaction:
                if latest_transaction["secmen_sayisi"] != self.current_total_voters:
                    if not messagebox.askyesno("Uyarı", 
                        f"Toplam seçmen sayısı farklı!\n"
                        f"Önceki kayıt: {latest_transaction['secmen_sayisi']}\n"
                        f"Sizin girdiğiniz: {self.current_total_voters}\n\n"
                        f"Kaydetmeye devam etmek istiyor musunuz?"):
                        return
            
            # Oy takibi için zaman damgası
            vote_tracking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Blockchain'e kaydet
            takip_verisi = {
                "sandik_no": sandik_no,
                "salon_no": self.current_salon,
                "secmen_sayisi": self.current_total_voters,
                "katilan_secmen": katilan_secmen,
                "gözlemci_id": self.current_observer.observer_id,
                "timestamp": vote_tracking_time,
                "oy_kullananlar": oy_kullananlar,
                "last_updater_vote_tracking": self.current_observer.name,
                "last_update_time_vote_tracking": vote_tracking_time,
                "islem_turu": "oy_takibi"  # İşlem türünü belirt
            }
            
            self.chain.add_transaction(takip_verisi, self.current_observer.observer_id)
            self.chain.mine_pending_transanction()
            
            messagebox.showinfo("Başarılı", f"Seçmen kayıtları başarıyla kaydedildi.\n\nGüncelleyen: {self.current_observer.name}\nGüncelleme Zamanı: {vote_tracking_time}")
            self.log(f"Seçmen kayıtları blockchain'e kaydedildi: {sandik_no}")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıt sırasında hata oluştu: {str(e)}")
            return

    def save_party_votes(self):
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
        
        if not self.current_sandik or not self.current_salon:
            messagebox.showerror("Hata", "Lütfen önce sandık ve salon seçin!")
            return
        
        # Parti oylarını al
        party_votes = {}
        total_votes = 0
        
        for party, entry in self.party_entries.items():
            try:
                votes = int(entry.get())
                party_votes[party] = votes
                total_votes += votes
            except ValueError:
                messagebox.showerror("Hata", f"Lütfen {party} için geçerli bir oy sayısı girin!")
                return
        
        # Veriyi hazırla
        party_votes_data = {
            "islem_turu": "parti_oylari",
                "sandik_no": self.current_sandik,
                "salon_no": self.current_salon,
            "gözlemci_id": self.current_observer.observer_id,
            "gözlemci_ad": self.current_observer.name,
            "party_votes": party_votes,  # Parti oylarını ekle
                "total_votes": total_votes,
                "last_updater_party_votes": self.current_observer.name,
            "last_update_time_party_votes": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        # Debug için
        print(f"\n=== PARTİ OYLARI VERİSİ ===")
        print(party_votes_data)
            
        # Veriyi blockchain'e ekle
        self.chain.add_transaction(party_votes_data)
            
        # Yeni blok oluştur
        self.chain.mine_pending_transanction()
            
        messagebox.showinfo("Başarılı", "Parti oyları kaydedildi!")
            
    def show_chain(self):
        """Blockchain'i görüntüle"""
        # Mevcut pencereyi temizle
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Başlık
        title_label = ttk.Label(self.main_frame, text="Blockchain Görüntüleme", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Text widget oluştur
        text_widget = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, width=80, height=30)
        text_widget.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Blockchain'i görüntüle
        chain_text = self.chain.print_chain()
        text_widget.insert("1.0", chain_text)
        text_widget.configure(state="disabled")
        
        # Geri dön butonu
        ttk.Button(self.main_frame, text="Geri Dön", command=lambda: [self.setup_gui(), self.selection_frame.grid(), 
            self.selection_salon_label.configure(text=self.current_salon),
            self.selection_sandik_label.configure(text=self.current_sandik),
            self.selection_total_voters_label.configure(text=str(self.current_total_voters))]).pack(pady=10)

    def back_to_operations(self):
        """İşlemler ekranına geri dön"""
        # Mevcut pencereyi temizle
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # GUI'yi yeniden kur
        self.setup_gui()
        
        # İşlemler ekranını göster
        self.operations_frame.grid()
        self.selection_frame.grid_remove()
        self.location_frame.grid_remove()
        self.vote_tracking_frame.grid_remove()
        self.party_votes_frame.grid_remove()
        
        # Rapor frame'ini göster
        self.report_frame.grid()
        
    def show_report(self):
        # Rapor penceresi
        report_window = tk.Toplevel(self.root)
        report_window.title("Seçim Raporu")
        report_window.geometry("800x600")
        
        # Text widget
        text_widget = scrolledtext.ScrolledText(report_window, wrap=tk.WORD)
        text_widget.pack(expand=True, fill=tk.BOTH)
        
        # Rapor metni
        report_text = "SEÇİM RAPORU\n\n"
        
        # Tüm sandıkların verilerini topla
        sandik_data = {}
        
        for block in self.chain.chain:
            for transaction in block.data:
                if isinstance(transaction, dict) and "sandik_no" in transaction:
                    sandik_no = transaction["sandik_no"]
                    salon_no = transaction["salon_no"]
                    key = f"{salon_no}-{sandik_no}"
                    
                    if key not in sandik_data:
                        sandik_data[key] = {
                            "salon_no": salon_no,
                            "sandik_no": sandik_no,
                            "party_votes": {},
                            "total_votes": 0,
                            "last_update": None,
                            "vote_tracking": {
                                "secmen_sayisi": 0,
                                "oy_kullananlar": [],
                                "last_updater": None,
                                "last_update_time": None
                            }
                        }
                    
                    # Parti oyları verilerini al
                    if transaction.get("islem_turu") == "parti_oylari":
                        party_votes = transaction.get("party_votes", {})
                        total_votes = transaction.get("total_votes", 0)
                        timestamp = transaction.get("timestamp")
                        
                        if sandik_data[key]["last_update"] is None or timestamp > sandik_data[key]["last_update"]:
                            sandik_data[key]["party_votes"] = party_votes
                            sandik_data[key]["total_votes"] = total_votes
                            sandik_data[key]["last_update"] = timestamp
                
                    # Oy takibi verilerini al
                    if transaction.get("islem_turu") == "oy_takibi":
                        secmen_sayisi = transaction.get("secmen_sayisi", 0)
                        oy_kullananlar = transaction.get("oy_kullananlar", [])
                        last_updater = transaction.get("last_updater_vote_tracking")
                        last_update_time = transaction.get("last_update_time_vote_tracking")
                        timestamp = transaction.get("timestamp")
                        
                        if sandik_data[key]["last_update"] is None or timestamp > sandik_data[key]["last_update"]:
                            sandik_data[key]["vote_tracking"] = {
                                "secmen_sayisi": secmen_sayisi,
                                "oy_kullananlar": oy_kullananlar,
                                "last_updater": last_updater,
                                "last_update_time": last_update_time
                            }
                            sandik_data[key]["last_update"] = timestamp
        
        # Raporu oluştur
        for key, data in sorted(sandik_data.items()):
            report_text += f"Salon: {data['salon_no']}, Sandık: {data['sandik_no']}\n"
            
            # Oy takibi bilgileri
            vote_tracking = data["vote_tracking"]
            if vote_tracking["secmen_sayisi"] > 0:
                report_text += "Oy Takibi:\n"
                report_text += f"  Toplam Seçmen: {vote_tracking['secmen_sayisi']}\n"
                report_text += f"  Katılan Seçmen: {len(vote_tracking['oy_kullananlar'])}\n"
                katilim_orani = (len(vote_tracking['oy_kullananlar']) / vote_tracking['secmen_sayisi'] * 100) if vote_tracking['secmen_sayisi'] > 0 else 0
                report_text += f"  Katılım Oranı: {katilim_orani:.1f}%\n"
                report_text += f"  Oy Kullananlar: {', '.join(map(str, vote_tracking['oy_kullananlar']))}\n"
                report_text += f"  Son Güncelleyen: {vote_tracking['last_updater']}\n"
                report_text += f"  Son Güncelleme: {vote_tracking['last_update_time']}\n\n"
            
            # Parti oyları bilgileri
            report_text += "Parti Oyları:\n"
            party_votes = data["party_votes"]
            if party_votes:  # Parti oyları varsa
                for party, votes in sorted(party_votes.items()):
                    report_text += f"  {party}: {votes} oy\n"
                report_text += f"  Toplam: {data['total_votes']} oy\n"
            else:  # Parti oyları yoksa
                report_text += "  Henüz oy girişi yapılmamış.\n"
            
            report_text += "\n"
        
        # Metni widget'a ekle
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, report_text)
        text_widget.configure(state='disabled')

    def check_chain(self):
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
            
        if self.chain.is_chain_valid():
            messagebox.showinfo("Zincir Kontrolü", "Zincir güvende")
        else:
            messagebox.showerror("Zincir Kontrolü", "Zincir geçersiz! Veriler kurcalanmış olabilir")
            
    def on_closing(self):
        if messagebox.askokcancel("Çıkış", "Uygulamayı kapatmak istediğinizden emin misiniz?"):
            self.node.stop()
            self.root.destroy()

    def add_party_row(self, party_name):
        # Yeni parti için frame
        row = len(self.party_votes)
        party_frame = ttk.Frame(self.party_list_frame)
        party_frame.grid(row=row, column=0, pady=2, sticky='w')
        
        # Parti adı ve oy sayısı
        ttk.Label(party_frame, text=party_name).grid(row=0, column=0, padx=5)
        vote_label = ttk.Label(party_frame, text="0")
        vote_label.grid(row=0, column=1, padx=5)
        
        # Azaltma butonu
        minus_btn = ttk.Button(party_frame, text="-", width=3)
        minus_btn.configure(command=lambda p=party_name: self.decrement_party_vote(p))
        minus_btn.grid(row=0, column=2, padx=5)
        
        # Artırma butonu
        plus_btn = ttk.Button(party_frame, text="+", width=3)
        plus_btn.configure(command=lambda p=party_name: self.increment_party_vote(p))
        plus_btn.grid(row=0, column=3, padx=5)
        
        # Parti bilgilerini kaydet
        self.party_votes[party_name] = 0
        self.party_vote_labels[party_name] = vote_label

    def increment_party_vote(self, party_name):
        if party_name in self.party_votes:
            self.party_votes[party_name] += 1
            self.party_vote_labels[party_name].configure(text=str(self.party_votes[party_name]))
            # Toplam oy sayısını güncelle
            total_votes = sum(self.party_votes.values())
            self.total_votes_label.configure(text=str(total_votes))
        else:
            messagebox.showerror("Hata", "Bu parti eklenmemiş!")

    def decrement_party_vote(self, party_name):
        if party_name in self.party_votes:
            if self.party_votes[party_name] > 0:
                self.party_votes[party_name] -= 1
                self.party_vote_labels[party_name].configure(text=str(self.party_votes[party_name]))
                # Toplam oy sayısını güncelle
                total_votes = sum(self.party_votes.values())
                self.total_votes_label.configure(text=str(total_votes))
        else:
            messagebox.showerror("Hata", "Bu parti eklenmemiş!") 
            messagebox.showwarning("Uyarı", "Oy sayısı 0'dan küçük olamaz!")

    def logout(self):
        # Mevcut gözlemciyi temizle
        self.current_observer = None
        self.current_salon = None
        self.current_sandik = None
        
        # Tüm frame'leri gizle
        self.location_frame.grid_remove()
        self.selection_frame.grid_remove()
        self.operations_frame.grid_remove()
        self.vote_tracking_frame.grid_remove()
        self.party_votes_frame.grid_remove()
        
        # Giriş frame'ini göster
        self.login_frame.grid()
        
        # Giriş alanını temizle
        self.observer_id_entry.delete(0, tk.END)
        
        # Seçmen sayısı alanlarını sıfırla
        self.secmen_sayisi_entry.configure(state='normal')
        self.katilan_secmen_entry.configure(state='normal')
        self.secmen_sayisi_entry.delete(0, tk.END)
        self.katilan_secmen_entry.delete(0, tk.END)
        
        # Sandık numarası alanlarını sıfırla
        self.sandik_no_entry.configure(state='normal')
        self.party_sandik_no_entry.configure(state='normal')
        self.sandik_no_entry.delete(0, tk.END)
        self.party_sandik_no_entry.delete(0, tk.END)
        
        # Listeleri temizle
        self.oy_kullananlar_list.delete("1.0", tk.END)
        
        # Sayaçı sıfırla
        self.voter_count = 0
        self.voter_count_label.config(text="Eklenen Seçmen: 0")
        
        # Bilgi etiketlerini sıfırla
        self.selection_salon_label.configure(text="-")
        self.selection_sandik_label.configure(text="-")
        self.selection_total_voters_label.configure(text="-")
        
        # Kaydet butonunu devre dışı bırak
        self.save_tracking_button.configure(state='disabled')
        
        self.log("Çıkış yapıldı")
        messagebox.showinfo("Bilgi", "Başarıyla çıkış yapıldı.")
        
    def edit_location(self):
        # İşlem seçim ekranını gizle
        self.selection_frame.grid_remove()
        
        # Konum seçim ekranını göster
        self.location_frame.grid()
        
        # Mevcut değerleri doldur
        self.location_salon_no_entry.delete(0, tk.END)
        self.location_salon_no_entry.insert(0, self.current_salon)
        
        self.location_sandik_no_entry.delete(0, tk.END)
        self.location_sandik_no_entry.insert(0, self.current_sandik)
        
        self.location_total_voters_entry.delete(0, tk.END)
        self.location_total_voters_entry.insert(0, str(self.current_total_voters))
        
        self.log("Konum bilgileri düzenleme moduna alındı")

    def back_to_location(self):
        # İşlem seçim ekranını göster
        self.selection_frame.grid()
        
        # İşlem frame'lerini gizle
        self.operations_frame.grid_remove()
        self.vote_tracking_frame.grid_remove()
        self.party_votes_frame.grid_remove()
        
        # Rapor frame'ini göster
        self.report_frame.grid()
        
        # Bilgileri güncelle
        self.selection_salon_label.configure(text=self.current_salon)
        self.selection_sandik_label.configure(text=self.current_sandik)
        self.selection_total_voters_label.configure(text=str(self.current_total_voters))
        
        self.log("İşlemler ekranına dönüldü")

    def check_conflicts(self):
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
            
        if not self.current_sandik or not self.current_salon:
            messagebox.showerror("Hata", "Lütfen önce sandık ve salon seçin!")
            return
            
        # Sandık için tüm işlemleri topla
        sandik_transactions = []
        for block in self.chain.chain:
            for transaction in block.transactions:
                if isinstance(transaction, dict) and "sandik_no" in transaction:
                    if transaction["sandik_no"] == self.current_sandik and transaction["salon_no"] == self.current_salon:
                        sandik_transactions.append(transaction)
        
        if not sandik_transactions:
            messagebox.showinfo("Bilgi", "Bu sandık için henüz kayıt bulunmuyor.")
            return
            
        # Çakışma kontrolü
        conflicts = []
        for i, trans1 in enumerate(sandik_transactions):
            for trans2 in sandik_transactions[i+1:]:
                # Seçmen listesi çakışması kontrolü
                if "oy_kullananlar" in trans1 and "oy_kullananlar" in trans2:
                    if set(trans1["oy_kullananlar"]) != set(trans2["oy_kullananlar"]):
                        conflict = {
                            "type": "seçmen_listesi",
                            "trans1": trans1,
                            "trans2": trans2,
                            "diff1": set(trans1["oy_kullananlar"]) - set(trans2["oy_kullananlar"]),
                            "diff2": set(trans2["oy_kullananlar"]) - set(trans1["oy_kullananlar"])
                        }
                        conflicts.append(conflict)
                
                # Parti oyları çakışması kontrolü
                if "party_votes" in trans1 and "party_votes" in trans2:
                    if trans1["party_votes"] != trans2["party_votes"]:
                        conflict = {
                            "type": "parti_oyları",
                            "trans1": trans1,
                            "trans2": trans2,
                            "diff1": {k: v for k, v in trans1["party_votes"].items() if k not in trans2["party_votes"] or trans2["party_votes"][k] != v},
                            "diff2": {k: v for k, v in trans2["party_votes"].items() if k not in trans1["party_votes"] or trans1["party_votes"][k] != v}
                        }
                        conflicts.append(conflict)
        
        if not conflicts:
            messagebox.showinfo("Bilgi", "Bu sandık için çakışma bulunmuyor.")
            return
            
        # Çakışmaları göster
        conflict_window = tk.Toplevel(self.root)
        conflict_window.title("Çakışma Raporu")
        conflict_window.geometry("800x600")
        
        text_widget = scrolledtext.ScrolledText(conflict_window)
        text_widget.pack(expand=True, fill=tk.BOTH)
        
        conflict_text = f"ÇAKIŞMA RAPORU - Salon: {self.current_salon}, Sandık: {self.current_sandik}\n\n"
        
        for conflict in conflicts:
            conflict_text += "="*50 + "\n"
            if conflict["type"] == "seçmen_listesi":
                conflict_text += "SEÇMEN LİSTESİ ÇAKIŞMASI\n"
                conflict_text += f"Gözlemci 1: {conflict['trans1']['gözlemci_id']} - {conflict['trans1']['timestamp']}\n"
                conflict_text += f"Gözlemci 2: {conflict['trans2']['gözlemci_id']} - {conflict['trans2']['timestamp']}\n\n"
                
                if conflict["diff1"]:
                    conflict_text += f"Gözlemci 1'de olup Gözlemci 2'de olmayan seçmenler:\n"
                    for voter in conflict["diff1"]:
                        conflict_text += f"- {voter}\n"
                
                if conflict["diff2"]:
                    conflict_text += f"\nGözlemci 2'de olup Gözlemci 1'de olmayan seçmenler:\n"
                    for voter in conflict["diff2"]:
                        conflict_text += f"- {voter}\n"
                        
            elif conflict["type"] == "parti_oyları":
                conflict_text += "PARTİ OYLARI ÇAKIŞMASI\n"
                conflict_text += f"Gözlemci 1: {conflict['trans1']['gözlemci_id']} - {conflict['trans1']['timestamp']}\n"
                conflict_text += f"Gözlemci 2: {conflict['trans2']['gözlemci_id']} - {conflict['trans2']['timestamp']}\n\n"
                
                if conflict["diff1"]:
                    conflict_text += f"Gözlemci 1'in oyları:\n"
                    for party, votes in conflict["diff1"].items():
                        conflict_text += f"- {party}: {votes} oy\n"
                
                if conflict["diff2"]:
                    conflict_text += f"\nGözlemci 2'nin oyları:\n"
                    for party, votes in conflict["diff2"].items():
                        conflict_text += f"- {party}: {votes} oy\n"
            
            conflict_text += "\n"
        
        text_widget.insert(tk.END, conflict_text)

    def show_ballot_box_details(self):
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
            
        # Her sandık için en son işlemleri tutacak sözlükler
        latest_vote_tracking = {}
        latest_party_votes = {}
        
        # Önce her sandık için en son işlemleri bul
        for block in self.chain.chain:
            for transaction in block.transactions:
                if isinstance(transaction, dict) and "sandik_no" in transaction:
                    try:
                        sandik_no = transaction.get("sandik_no")
                        salon_no = transaction.get("salon_no")
                        key = f"{salon_no}_{sandik_no}"  # Salon ve sandık numarasını birleştir
                        
                        if "timestamp" in transaction:
                            current_timestamp = datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
                            
                            # Oy takibi işlemi
                            if "last_update_time_vote_tracking" in transaction:
                                if key not in latest_vote_tracking or current_timestamp > datetime.strptime(latest_vote_tracking[key]["last_update_time_vote_tracking"], "%Y-%m-%d %H:%M:%S"):
                                    latest_vote_tracking[key] = transaction
                            
                            # Parti oyları işlemi
                            if "last_update_time_party_votes" in transaction:
                                if key not in latest_party_votes or current_timestamp > datetime.strptime(latest_party_votes[key]["last_update_time_party_votes"], "%Y-%m-%d %H:%M:%S"):
                                    latest_party_votes[key] = transaction
                                    
                    except (ValueError, TypeError) as e:
                        continue
        
        if not latest_vote_tracking and not latest_party_votes:
            messagebox.showinfo("Bilgi", "Henüz kayıtlı sandık bulunmuyor.")
            return
            
        # Detaylı rapor penceresi
        details_window = tk.Toplevel(self.root)
        details_window.title("Sandık Sandık Oy Sayımı")
        details_window.geometry("800x600")
        
        # Arama çerçevesi
        search_frame = tk.Frame(details_window)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        search_label = tk.Label(search_frame, text="Ara:")
        search_label.pack(side=tk.LEFT)
        
        search_entry = tk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        text_widget = scrolledtext.ScrolledText(details_window)
        text_widget.pack(expand=True, fill=tk.BOTH)
        
        details_text = "SANDIK SANDIK OY SAYIMI\n\n"
        
        # Her sandık için detaylı bilgileri ekle (en son eklenenler en üstte)
        all_keys = sorted(set(list(latest_vote_tracking.keys()) + list(latest_party_votes.keys())), 
                         key=lambda x: max(
                             datetime.strptime(latest_vote_tracking.get(x, {}).get("timestamp", "2000-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"),
                             datetime.strptime(latest_party_votes.get(x, {}).get("timestamp", "2000-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
                         ), reverse=True)
        
        for key in all_keys:
            salon_no, sandik_no = key.split("_")
            
            details_text += f"Sandık No: {sandik_no}\n"
            details_text += f"  Salon No: {salon_no}\n"
            
            # Oy takibi bilgileri
            if key in latest_vote_tracking:
                transaction = latest_vote_tracking[key]
                details_text += f"  Oy Takibi Son Güncelleyen: {transaction['last_updater_vote_tracking']} (ID: {transaction.get('gözlemci_id', 'Bilinmiyor')})\n"
                details_text += f"  Oy Takibi Son Güncelleme: {transaction['last_update_time_vote_tracking']}\n\n"
                
                # Seçmen bilgileri
                secmen_sayisi = transaction.get("secmen_sayisi", 0)
                katilan_secmen = len(transaction.get("oy_kullananlar", []))
                katilim_orani = (katilan_secmen / secmen_sayisi * 100) if secmen_sayisi > 0 else 0
                
                details_text += f"  Toplam Seçmen: {secmen_sayisi}\n"
                details_text += f"  Katılan Seçmen: {katilan_secmen}\n"
                details_text += f"  Katılım Oranı: {katilim_orani:.1f}%\n"
                
                # Oy kullananlar
                oy_kullananlar = transaction.get("oy_kullananlar", [])
                details_text += f"  Oy Kullananlar: {', '.join(oy_kullananlar)}\n\n"
            
            # Parti oyları bilgileri
            if key in latest_party_votes:
                transaction = latest_party_votes[key]
                details_text += f"  Parti Oyları Son Güncelleyen: {transaction['last_updater_party_votes']} (ID: {transaction.get('gözlemci_id', 'Bilinmiyor')})\n"
                details_text += f"  Parti Oyları Son Güncelleme: {transaction['last_update_time_party_votes']}\n"
                
                details_text += "  Parti Oyları:\n"
                party_votes = transaction.get("party_votes", {})
                for party, votes in sorted(party_votes.items()):
                    details_text += f"    {party}: {votes} oy\n"
                details_text += f"    Toplam: {transaction.get('total_votes', 0)} oy\n"
            
            details_text += "\n" + "="*50 + "\n\n"
        
        text_widget.insert(tk.END, details_text)
        text_widget.configure(state='disabled')  # Metni salt okunur yap
        
        # Arama fonksiyonu
        def search_text(event=None):
            search_term = search_entry.get().lower()
            text_widget.configure(state='normal')
            text_widget.delete(1.0, tk.END)
            
            # Orijinal metni satırlara böl
            lines = details_text.split('\n')
            
            # Arama terimini içeren satırları bul ve vurgula
            for i, line in enumerate(lines):
                if search_term in line.lower():
                    # Arama terimini bulunan satıra yönlendir
                    text_widget.insert(tk.END, '\n'.join(lines))
                    text_widget.see(f"{i+1}.0")
                    text_widget.tag_add("search", f"{i+1}.0", f"{i+1}.end")
                    text_widget.tag_config("search", background="yellow")
                    break
            else:
                # Eğer arama terimi bulunamazsa tüm metni göster
                text_widget.insert(tk.END, '\n'.join(lines))
            
            text_widget.configure(state='disabled')
        
        # Arama girişine Enter tuşu ile arama yapma özelliği ekle
        search_entry.bind('<Return>', search_text)
        
        # Arama butonu
        search_button = tk.Button(search_frame, text="Ara", command=search_text)
        search_button.pack(side=tk.LEFT, padx=5)

    def show_observer_records(self):
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
            
        # Gözlemcinin girdiği tüm işlemleri ve her sandık için en son işlemleri tutacak sözlükler
        observer_transactions = {}
        latest_transactions = {}
        
        # Tüm işlemleri topla
        for block in self.chain.chain:
            for transaction in block.transactions:
                if isinstance(transaction, dict) and "sandik_no" in transaction:
                    try:
                        sandik_no = transaction.get("sandik_no")
                        salon_no = transaction.get("salon_no")
                        key = f"{salon_no}_{sandik_no}"
                        
                        # Gözlemcinin kendi işlemlerini kaydet
                        if transaction.get("gözlemci_id") == self.current_observer.observer_id:
                            if key not in observer_transactions or datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S") > datetime.strptime(observer_transactions[key]["timestamp"], "%Y-%m-%d %H:%M:%S"):
                                observer_transactions[key] = transaction
                        
                        # Her sandık için en son işlemi kaydet
                        if "timestamp" in transaction:
                            current_timestamp = datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
                            if key not in latest_transactions or current_timestamp > datetime.strptime(latest_transactions[key]["timestamp"], "%Y-%m-%d %H:%M:%S"):
                                latest_transactions[key] = transaction
                    except (ValueError, TypeError) as e:
                        continue
        
        if not observer_transactions:
            messagebox.showinfo("Bilgi", "Henüz kayıt yapmadınız.")
            return
            
        # Detaylı rapor penceresi
        details_window = tk.Toplevel(self.root)
        details_window.title("Benim Gözlemlerim")
        details_window.geometry("800x600")
        
        # Text widget
        text_widget = scrolledtext.ScrolledText(details_window, wrap=tk.WORD)
        text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        details_text = f"GÖZLEMCİ: {self.current_observer.name} (ID: {self.current_observer.observer_id})\n\n"
        
        # Her sandık için detaylı bilgileri ekle (en son eklenenler en altta)
        for key, transaction in sorted(observer_transactions.items(), key=lambda x: datetime.strptime(x[1]["timestamp"], "%Y-%m-%d %H:%M:%S")):
            salon_no, sandik_no = key.split("_")
            
            details_text += f"Sandık No: {sandik_no}\n"
            details_text += f"  Salon No: {salon_no}\n"
            details_text += f"  Son Kaydetme Zamanı: {transaction['timestamp']}\n\n"
            
            # Seçmen bilgileri
            secmen_sayisi = transaction.get("secmen_sayisi", 0)
            katilan_secmen = len(transaction.get("oy_kullananlar", []))
            katilim_orani = (katilan_secmen / secmen_sayisi * 100) if secmen_sayisi > 0 else 0
            
            details_text += f"  Toplam Seçmen: {secmen_sayisi}\n"
            details_text += f"  Katılan Seçmen: {katilan_secmen}\n"
            details_text += f"  Katılım Oranı: {katilim_orani:.1f}%\n"
            
            # Oy kullananlar
            oy_kullananlar = transaction.get("oy_kullananlar", [])
            details_text += f"  Oy Kullananlar: {', '.join(oy_kullananlar)}\n"
            
            # Parti oyları
            if "party_votes" in transaction:
                details_text += "  Parti Oyları:\n"
                party_votes = transaction.get("party_votes", {})
                for party, votes in sorted(party_votes.items()):
                    details_text += f"    {party}: {votes} oy\n"
                details_text += f"    Toplam: {transaction.get('total_votes', 0)} oy\n"
            
            # Son girilen veriyle karşılaştırma
            if key in latest_transactions and latest_transactions[key] != transaction:
                latest = latest_transactions[key]
                details_text += "\n  FARKLILIKLAR:\n"
                
                # Seçmen listesi farklılıkları
                if set(transaction.get("oy_kullananlar", [])) != set(latest.get("oy_kullananlar", [])):
                    details_text += "  Seçmen Listesi Farklılıkları:\n"
                    my_voters = set(transaction.get("oy_kullananlar", []))
                    latest_voters = set(latest.get("oy_kullananlar", []))
                    if my_voters - latest_voters:
                        details_text += f"    Sizin listede olup son listede olmayanlar: {', '.join(my_voters - latest_voters)}\n"
                    if latest_voters - my_voters:
                        details_text += f"    Son listede olup sizin listenizde olmayanlar: {', '.join(latest_voters - my_voters)}\n"
                
                # Parti oyları farklılıkları
                if "party_votes" in transaction and "party_votes" in latest:
                    if transaction["party_votes"] != latest["party_votes"]:
                        details_text += "  Parti Oyları Farklılıkları:\n"
                        my_votes = transaction["party_votes"]
                        latest_votes = latest["party_votes"]
                        for party in set(my_votes.keys()) | set(latest_votes.keys()):
                            my_vote = my_votes.get(party, 0)
                            latest_vote = latest_votes.get(party, 0)
                            if my_vote != latest_vote:
                                details_text += f"    {party}: Sizin girişiniz: {my_vote}, Son giriş: {latest_vote}\n"
                
                details_text += f"  Son giriş zamanı: {latest['timestamp']}\n"
                details_text += f"  Son girişi yapan gözlemci: {latest['gözlemci_id']}\n"
            
            details_text += "\n" + "="*50 + "\n\n"
        
        # Text widget'a metni ekle
        text_widget.insert(tk.END, details_text)
        text_widget.configure(state='disabled')  # Metni salt okunur yap
        
        # Arama çerçevesi
        search_frame = ttk.Frame(details_window)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        search_label = ttk.Label(search_frame, text="Ara:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Arama fonksiyonu
        def search_text(event=None):
            search_term = search_entry.get().lower()
            text_widget.configure(state='normal')
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, details_text)
            
            # Arama terimini içeren satırları bul ve vurgula
            start_pos = "1.0"
            while True:
                pos = text_widget.search(search_term, start_pos, tk.END, nocase=True)
                if not pos:
                    break
                line_start = pos.split('.')[0]
                line_end = text_widget.index(f"{line_start}.end")
                text_widget.tag_add("search", pos, line_end)
                text_widget.tag_config("search", background="yellow")
                start_pos = line_end
            
            text_widget.configure(state='disabled')
        
        # Arama girişine Enter tuşu ile arama yapma özelliği ekle
        search_entry.bind('<Return>', search_text)
        
        # Arama butonu
        search_button = ttk.Button(search_frame, text="Ara", command=search_text)
        search_button.pack(side=tk.LEFT, padx=5)

    def compare_selected_ballot(self):
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
            
        if not self.current_sandik or not self.current_salon:
            messagebox.showerror("Hata", "Lütfen önce sandık ve salon seçin!")
            return
            
        # Debug için
        print(f"\n=== DEBUG BAŞLANGIÇ ===")
        print(f"Sandık No: {self.current_sandik}, Salon No: {self.current_salon}")
        print(f"Gözlemci ID: {self.current_observer.observer_id}")
        
        # Gözlemcinin son girdiği verileri bul
        observer_last_vote_tracking = None
        observer_last_party_votes = None
        observer_last_vote_tracking_time = None
        observer_last_party_votes_time = None
        
        # Sandığın son durumlarını bul
        latest_vote_tracking = None
        latest_party_votes = None
        latest_vote_tracking_time = None
        latest_party_votes_time = None
        
        # Blockchain'deki tüm blokları kontrol et
        for block_index, block in enumerate(self.chain.chain):
            print(f"\nBlok {block_index} kontrol ediliyor...")
            for transaction_index, transaction in enumerate(block.data):
                if isinstance(transaction, dict) and "sandik_no" in transaction:
                    if transaction["sandik_no"] == self.current_sandik and transaction["salon_no"] == self.current_salon:
                        print(f"\nİşlem bulundu (Blok {block_index}, İşlem {transaction_index}):")
                        print(f"İşlem türü: {transaction.get('islem_turu')}")
                        print(f"Gözlemci ID: {transaction.get('gözlemci_id')}")
                        print(f"Timestamp: {transaction.get('timestamp')}")
                        
                        try:
                            current_timestamp = datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
                        except (ValueError, TypeError) as e:
                            print(f"Timestamp hatası: {e}")
                            continue
                        
                        # Gözlemcinin son işlemlerini bul
                        if transaction.get("gözlemci_id") == self.current_observer.observer_id:
                            print("Gözlemcinin işlemi bulundu!")
                            # Oy takibi işlemi
                            if transaction.get("islem_turu") == "oy_takibi":
                                if observer_last_vote_tracking_time is None or current_timestamp > observer_last_vote_tracking_time:
                                    observer_last_vote_tracking_time = current_timestamp
                                    observer_last_vote_tracking = transaction
                                    print("Oy takibi güncellendi!")
                            
                            # Parti oyları işlemi
                            if transaction.get("islem_turu") == "parti_oylari":
                                if observer_last_party_votes_time is None or current_timestamp > observer_last_party_votes_time:
                                    observer_last_party_votes_time = current_timestamp
                                    observer_last_party_votes = transaction
                                    print("Parti oyları güncellendi!")
                        
                        # Sandığın son durumlarını bul
                        # Oy takibi işlemi
                        if transaction.get("islem_turu") == "oy_takibi":
                            if latest_vote_tracking_time is None or current_timestamp > latest_vote_tracking_time:
                                latest_vote_tracking_time = current_timestamp
                                latest_vote_tracking = transaction
                                print("En son oy takibi güncellendi!")
                        
                        # Parti oyları işlemi
                        if transaction.get("islem_turu") == "parti_oylari":
                            if latest_party_votes_time is None or current_timestamp > latest_party_votes_time:
                                latest_party_votes_time = current_timestamp
                                latest_party_votes = transaction
                                print("En son parti oyları güncellendi!")
        
        print("\n=== BULUNAN VERİLER ===")
        print(f"Observer last vote tracking: {observer_last_vote_tracking}")
        print(f"Observer last party votes: {observer_last_party_votes}")
        print(f"Latest vote tracking: {latest_vote_tracking}")
        print(f"Latest party votes: {latest_party_votes}")
        
        if not observer_last_vote_tracking and not observer_last_party_votes:
            messagebox.showinfo("Bilgi", "Bu sandık için henüz kayıt yapmadınız.")
            return
            
        if not latest_vote_tracking and not latest_party_votes:
            messagebox.showinfo("Bilgi", "Bu sandık için henüz kayıt bulunmuyor.")
            return
        
        # Karşılaştırma penceresi
        compare_window = tk.Toplevel(self.root)
        compare_window.title("Sandık Karşılaştırması")
        compare_window.geometry("800x600")
        
        # Text widget'ı oluştur
        text_widget = scrolledtext.ScrolledText(compare_window, wrap=tk.WORD, width=80, height=30)
        text_widget.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Metni oluştur
        compare_text = f"SANDIK KARŞILAŞTIRMASI - Salon: {self.current_salon}, Sandık: {self.current_sandik}\n\n"
        
        # Gözlemcinin son girdiği veri
        compare_text += "BENİM GÖZLEMİM:\n"
        compare_text += f"Sandık No: {self.current_sandik}\n"
        compare_text += f"  Salon No: {self.current_salon}\n"
        
        # Oy takibi bilgileri
        if observer_last_party_votes:  # Parti oyları verilerinden oy takibi bilgilerini al
            compare_text += f"  Oy Takibi Son Güncelleyen: {observer_last_party_votes.get('last_updater_party_votes', 'Bilinmiyor')} (ID: {observer_last_party_votes.get('gözlemci_id', 'Bilinmiyor')})\n"
            compare_text += f"  Oy Takibi Son Güncelleme: {observer_last_party_votes.get('last_update_time_party_votes', 'Bilinmiyor')}\n\n"
            
            # Seçmen bilgileri
            secmen_sayisi = observer_last_party_votes.get("secmen_sayisi", 0)
            katilan_secmen = observer_last_party_votes.get("katilan_secmen", 0)
            katilim_orani = observer_last_party_votes.get("katilim_orani", 0)
            
            compare_text += f"  Toplam Seçmen: {secmen_sayisi}\n"
            compare_text += f"  Katılan Seçmen: {katilan_secmen}\n"
            compare_text += f"  Katılım Oranı: {katilim_orani:.1f}%\n"
            
            # Oy kullananlar
            oy_kullananlar = observer_last_party_votes.get("oy_kullananlar", [])
            compare_text += f"  Oy Kullananlar: {', '.join(map(str, oy_kullananlar))}\n\n"
        
        # Parti oyları bilgileri
        if observer_last_party_votes:
            compare_text += f"  Parti Oyları Son Güncelleyen: {observer_last_party_votes.get('last_updater_party_votes', 'Bilinmiyor')} (ID: {observer_last_party_votes.get('gözlemci_id', 'Bilinmiyor')})\n"
            compare_text += f"  Parti Oyları Son Güncelleme: {observer_last_party_votes.get('last_update_time_party_votes', 'Bilinmiyor')}\n"
            
            compare_text += "  Parti Oyları:\n"
            party_votes = observer_last_party_votes.get("party_votes", {})
            if party_votes:  # Parti oyları varsa
                for party, votes in sorted(party_votes.items()):
                    compare_text += f"    {party}: {votes} oy\n"
                compare_text += f"    Toplam: {observer_last_party_votes.get('total_votes', 0)} oy\n"
            else:  # Parti oyları yoksa
                compare_text += "    Henüz oy girişi yapılmamış.\n"
        
        compare_text += "\n" + "="*50 + "\n\n"
        
        # Sandığın son durumu
        compare_text += "SANDIK DURUMU:\n"
        compare_text += f"Sandık No: {self.current_sandik}\n"
        compare_text += f"  Salon No: {self.current_salon}\n"
        
        # Oy takibi bilgileri
        if latest_party_votes:  # Parti oyları verilerinden oy takibi bilgilerini al
            compare_text += f"  Oy Takibi Son Güncelleyen: {latest_party_votes.get('last_updater_party_votes', 'Bilinmiyor')} (ID: {latest_party_votes.get('gözlemci_id', 'Bilinmiyor')})\n"
            compare_text += f"  Oy Takibi Son Güncelleme: {latest_party_votes.get('last_update_time_party_votes', 'Bilinmiyor')}\n\n"
            
            # Seçmen bilgileri
            secmen_sayisi = latest_party_votes.get("secmen_sayisi", 0)
            katilan_secmen = latest_party_votes.get("katilan_secmen", 0)
            katilim_orani = latest_party_votes.get("katilim_orani", 0)
            
            compare_text += f"  Toplam Seçmen: {secmen_sayisi}\n"
            compare_text += f"  Katılan Seçmen: {katilan_secmen}\n"
            compare_text += f"  Katılım Oranı: {katilim_orani:.1f}%\n"
            
            # Oy kullananlar
            oy_kullananlar = latest_party_votes.get("oy_kullananlar", [])
            compare_text += f"  Oy Kullananlar: {', '.join(map(str, oy_kullananlar))}\n\n"
        
        # Parti oyları bilgileri
        if latest_party_votes:
            compare_text += f"  Parti Oyları Son Güncelleyen: {latest_party_votes.get('last_updater_party_votes', 'Bilinmiyor')} (ID: {latest_party_votes.get('gözlemci_id', 'Bilinmiyor')})\n"
            compare_text += f"  Parti Oyları Son Güncelleme: {latest_party_votes.get('last_update_time_party_votes', 'Bilinmiyor')}\n"
            
            compare_text += "  Parti Oyları:\n"
            party_votes = latest_party_votes.get("party_votes", {})
            if party_votes:  # Parti oyları varsa
                for party, votes in sorted(party_votes.items()):
                    compare_text += f"    {party}: {votes} oy\n"
                compare_text += f"    Toplam: {latest_party_votes.get('total_votes', 0)} oy\n"
            else:  # Parti oyları yoksa
                compare_text += "    Henüz oy girişi yapılmamış.\n"
        
        # Metni widget'a ekle
        text_widget.delete(1.0, tk.END)  # Önce mevcut içeriği temizle
        text_widget.insert(tk.END, compare_text)
        
        # Widget'ı güncelle ve salt okunur yap
        text_widget.update()
        text_widget.configure(state='disabled')
        
        # Pencereyi güncelle ve odakla
        compare_window.update()
        compare_window.focus_force()
        
        # Debug için widget içeriğini kontrol et
        print("\n=== WIDGET İÇERİĞİ ===")
        print(text_widget.get(1.0, tk.END))
        
        # Pencereyi ön plana getir
        compare_window.lift()
        compare_window.attributes('-topmost', True)
        compare_window.attributes('-topmost', False)

    def show_conflicts(self):
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
            
        # Her sandık için en son işlemleri tutacak sözlük
        latest_transactions = {}
        
        # Tüm işlemleri topla
        for block in self.chain.chain:
            for transaction in block.data:  # transactions yerine data kullanıyoruz
                if isinstance(transaction, dict) and "sandik_no" in transaction:
                    try:
                        sandik_no = transaction.get("sandik_no")
                        salon_no = transaction.get("salon_no")
                        key = f"{salon_no}_{sandik_no}"
                        
                        # Her sandık için en son işlemi kaydet
                        if "timestamp" in transaction:
                            current_timestamp = datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
                            if key not in latest_transactions or current_timestamp > datetime.strptime(latest_transactions[key]["timestamp"], "%Y-%m-%d %H:%M:%S"):
                                latest_transactions[key] = transaction
                    except (ValueError, TypeError) as e:
                        continue
        
        if not latest_transactions:
            messagebox.showinfo("Bilgi", "Henüz kayıt bulunmuyor.")
            return
            
        # Detaylı rapor penceresi
        details_window = tk.Toplevel(self.root)
        details_window.title("Farklılıklar")
        details_window.geometry("800x600")
        
        # Arama çerçevesi
        search_frame = tk.Frame(details_window)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        search_label = tk.Label(search_frame, text="Ara:")
        search_label.pack(side=tk.LEFT)
        
        search_entry = tk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        text_widget = scrolledtext.ScrolledText(details_window)
        text_widget.pack(expand=True, fill=tk.BOTH)
        
        details_text = "SANDIK FARKLILIKLARI\n\n"
        
        # Her sandık için detaylı bilgileri ekle
        for key, transaction in sorted(latest_transactions.items(), key=lambda x: datetime.strptime(x[1]["timestamp"], "%Y-%m-%d %H:%M:%S")):
            salon_no, sandik_no = key.split("_")
            
            details_text += f"Sandık No: {sandik_no}\n"
            details_text += f"  Salon No: {salon_no}\n"
            details_text += f"  Son Güncelleme: {transaction['timestamp']}\n"
            details_text += f"  Son Güncelleyen Gözlemci: {transaction['gözlemci_id']}\n\n"
            
            # Seçmen bilgileri
            secmen_sayisi = transaction.get("secmen_sayisi", 0)
            katilan_secmen = len(transaction.get("oy_kullananlar", []))
            katilim_orani = (katilan_secmen / secmen_sayisi * 100) if secmen_sayisi > 0 else 0
            
            details_text += f"  Toplam Seçmen: {secmen_sayisi}\n"
            details_text += f"  Katılan Seçmen: {katilan_secmen}\n"
            details_text += f"  Katılım Oranı: {katilim_orani:.1f}%\n"
            
            # Oy kullananlar
            oy_kullananlar = transaction.get("oy_kullananlar", [])
            details_text += f"  Oy Kullananlar: {', '.join(oy_kullananlar)}\n"
            
            # Parti oyları
            if "party_votes" in transaction:
                details_text += "  Parti Oyları:\n"
                party_votes = transaction.get("party_votes", {})
                for party, votes in sorted(party_votes.items()):
                    details_text += f"    {party}: {votes} oy\n"
                details_text += f"    Toplam: {transaction.get('total_votes', 0)} oy\n"
            
            # Aynı sandık ve salondaki diğer gözlemcilerin kayıtlarını bul
            other_observers_records = []
            for block in self.chain.chain:
                for other_transaction in block.transactions:
                    if isinstance(other_transaction, dict) and "sandik_no" in other_transaction:
                        if (other_transaction.get("sandik_no") == sandik_no and 
                            other_transaction.get("salon_no") == salon_no and 
                            other_transaction.get("gözlemci_id") != transaction.get("gözlemci_id")):
                            other_observers_records.append(other_transaction)
            
            if other_observers_records:
                details_text += "\n  DİĞER GÖZLEMCİLERİN KAYITLARI:\n"
                for other_record in other_observers_records:
                    details_text += f"\n    Gözlemci: {other_record['gözlemci_id']}\n"
                    details_text += f"    Kayıt Zamanı: {other_record['timestamp']}\n"
                    
                    # Seçmen listesi farklılıkları
                    if set(transaction.get("oy_kullananlar", [])) != set(other_record.get("oy_kullananlar", [])):
                        details_text += "    Seçmen Listesi Farklılıkları:\n"
                        current_voters = set(transaction.get("oy_kullananlar", []))
                        other_voters = set(other_record.get("oy_kullananlar", []))
                        if current_voters - other_voters:
                            details_text += f"      Son kayıtta olup bu kayıtta olmayanlar: {', '.join(current_voters - other_voters)}\n"
                        if other_voters - current_voters:
                            details_text += f"      Bu kayıtta olup son kayıtta olmayanlar: {', '.join(other_voters - current_voters)}\n"
                    
                    # Parti oyları farklılıkları
                    if "party_votes" in transaction and "party_votes" in other_record:
                        if transaction["party_votes"] != other_record["party_votes"]:
                            details_text += "    Parti Oyları Farklılıkları:\n"
                            current_votes = transaction["party_votes"]
                            other_votes = other_record["party_votes"]
                            for party in set(current_votes.keys()) | set(other_votes.keys()):
                                current_vote = current_votes.get(party, 0)
                                other_vote = other_votes.get(party, 0)
                                if current_vote != other_vote:
                                    details_text += f"      {party}: Son kayıt: {current_vote}, Bu kayıt: {other_vote}\n"
            
            details_text += "\n" + "="*50 + "\n\n"
        
        text_widget.insert(tk.END, details_text)
        text_widget.configure(state='disabled')  # Metni salt okunur yap
        
        # Arama fonksiyonu
        def search_text(event=None):
            search_term = search_entry.get().lower()
            text_widget.configure(state='normal')
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, details_text)
            
            # Arama terimini içeren satırları bul ve vurgula
            start_pos = "1.0"
            while True:
                pos = text_widget.search(search_term, start_pos, tk.END, nocase=True)
                if not pos:
                    break
                line_start = pos.split('.')[0]
                line_end = text_widget.index(f"{line_start}.end")
                text_widget.tag_add("search", pos, line_end)
                text_widget.tag_config("search", background="yellow")
                start_pos = line_end
            
            text_widget.configure(state='disabled')
        
        # Arama girişine Enter tuşu ile arama yapma özelliği ekle
        search_entry.bind('<Return>', search_text)
        
        # Arama butonu
        search_button = tk.Button(search_frame, text="Ara", command=search_text)
        search_button.pack(side=tk.LEFT, padx=5)

    def show_vote_count(self):
        """Oy sayımı ekranını göster"""
        # Mevcut pencereyi temizle
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Başlık
        title_label = ttk.Label(self.main_frame, text="Oy Sayımı", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Sonuçları al
        results = self.chain.count_votes()
        
        # Genel istatistikler
        stats_frame = ttk.LabelFrame(self.main_frame, text="Genel İstatistikler")
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(stats_frame, text=f"Toplam Seçmen: {results['toplam_secmen']}").pack(anchor="w", padx=5)
        ttk.Label(stats_frame, text=f"Toplam Katılım: {results['toplam_katilim']}").pack(anchor="w", padx=5)
        ttk.Label(stats_frame, text=f"Genel Katılım Oranı: {results['genel_katilim_orani']}%").pack(anchor="w", padx=5)
        
        # Parti oyları
        if results['parti_oylari']:
            party_frame = ttk.LabelFrame(self.main_frame, text="Parti Oyları")
            party_frame.pack(fill="x", padx=10, pady=5)
            
            for party, votes in results['parti_oylari'].items():
                ttk.Label(party_frame, text=f"{party}: {votes} oy").pack(anchor="w", padx=5)
        
        # Sandık detayları
        sandik_frame = ttk.LabelFrame(self.main_frame, text="Sandık Detayları")
        sandik_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview oluştur
        columns = ("Sandık No", "Seçmen Sayısı", "Katılan Seçmen", "Katılım Oranı", "Gözlemci Sayısı")
        tree = ttk.Treeview(sandik_frame, columns=columns, show="headings")
        
        # Sütun başlıkları
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Verileri ekle
        for sandik_no, data in results['sandiklar'].items():
            tree.insert("", "end", values=(
                sandik_no,
                data['secmen_sayisi'],
                data['katilan_secmen'],
                f"{data['katilim_orani']}%",
                len(data['gözlemciler'])
            ))
        
        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(sandik_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Yerleştir
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Geri dön butonu
        ttk.Button(self.main_frame, text="Geri Dön", command=self.show_main_menu).pack(pady=10)

    def show_main_menu(self):
        """Ana menüyü göster"""
        # Mevcut pencereyi temizle
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Başlık
        title_label = ttk.Label(self.main_frame, text="Seçim Gözlem Sistemi", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Menü butonları
        if not self.current_observer:
            ttk.Button(self.main_frame, text="Gözlemci Kaydı", command=self.show_observer_registration).pack(pady=5)
            ttk.Button(self.main_frame, text="Giriş Yap", command=self.show_login).pack(pady=5)
        else:
            ttk.Button(self.main_frame, text="Sandık Kaydı", command=self.show_sandik_registration).pack(pady=5)
            ttk.Button(self.main_frame, text="Oy Sayımı", command=self.show_vote_count).pack(pady=5)
            ttk.Button(self.main_frame, text="Zinciri Görüntüle", command=self.show_chain).pack(pady=5)
            ttk.Button(self.main_frame, text="Sandık Karşılaştırma", command=self.show_sandik_comparison).pack(pady=5)
            ttk.Button(self.main_frame, text="Çıkış Yap", command=self.logout).pack(pady=5)

    def show_sandik_registration(self):
        messagebox.showinfo("Sandık Kaydı", "Sandık kaydı ekranı henüz uygulanmadı.")

    def show_observer_registration(self):
        messagebox.showinfo("Gözlemci Kaydı", "Gözlemci kaydı ekranı henüz uygulanmadı.")

    def show_login(self):
        messagebox.showinfo("Giriş Yap", "Giriş ekranı zaten ana ekranda mevcut.")

    def show_sandik_comparison(self):
        messagebox.showinfo("Sandık Karşılaştırma", "Sandık karşılaştırma ekranı henüz uygulanmadı.")

    def add_vote(self):
        """Oy ekle"""
        if not self.current_observer:
            messagebox.showerror("Hata", "Lütfen önce giriş yapın!")
            return
            
        voter_id = self.vote_voter_id_entry.get().strip()
        party = self.vote_party_var.get()
        
        if not voter_id or not party:
            messagebox.showerror("Hata", "Lütfen seçmen ID ve parti seçin!")
            return
            
        try:
            voter_id = int(voter_id)
        except ValueError:
            messagebox.showerror("Hata", "Seçmen ID geçerli bir sayı olmalıdır!")
            return
            
        # Oy ekle
        try:
            response = requests.post('http://localhost:5000/add_vote', json={
                'observer_id': self.current_observer.id,
                'voter_id': voter_id,
                'salon_no': self.current_salon,
                'sandik_no': self.current_sandik,
                'party': party
            })
            
            if response.status_code == 200:
                # Seçmen sayısını güncelle
                self.voter_count += 1
                self.voter_count_label.config(text=str(self.voter_count))
                
                # Parti oylarını güncelle
                if party in self.party_votes:
                    self.party_votes[party] += 1
                else:
                    self.party_votes[party] = 1
                    
                # Parti oyları listesini güncelle
                self.update_party_votes_list()
                
                # Giriş alanlarını temizle
                self.vote_voter_id_entry.delete(0, tk.END)
                self.vote_party_var.set("")
                
                self.log(f"Oy eklendi - Seçmen: {voter_id}, Parti: {party}")
            else:
                error_data = response.json()
                messagebox.showerror("Hata", error_data.get('error', 'Oy eklenirken bir hata oluştu!'))
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Hata", f"Sunucu bağlantı hatası: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SeçimGözlemGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop() 