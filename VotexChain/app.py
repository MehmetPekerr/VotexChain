@app.route('/add_vote', methods=['POST'])
def add_vote():
    data = request.get_json()
    
    # Gerekli alanları kontrol et
    required_fields = ['observer_id', 'voter_id', 'salon_no', 'sandik_no', 'party']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Eksik bilgi'}), 400
    
    # Gözlemciyi kontrol et
    observer = Observer.query.get(data['observer_id'])
    if not observer:
        return jsonify({'error': 'Geçersiz gözlemci'}), 400
    
    # Blockchain üzerinde global oy kullanım kontrolü
    if chain.has_voted_anywhere(str(data['voter_id'])):
        return jsonify({'error': 'Bu seçmen herhangi bir sandıkta daha önce oy kullanmış'}), 400
    
    # Veritabanında oy kullanım kontrolü
    existing_vote = Transaction.query.filter_by(
        voter_id=data['voter_id']
    ).first()
    
    if existing_vote:
        return jsonify({'error': 'Bu seçmen daha önce oy kullanmış'}), 400
    
    # Yeni işlem oluştur
    transaction = Transaction(
        observer_id=data['observer_id'],
        voter_id=data['voter_id'],
        salon_no=data['salon_no'],
        sandik_no=data['sandik_no'],
        party=data['party'],
        timestamp=datetime.now()
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    # Blockchain'e ekle
    chain.add_transaction(transaction)
    
    return jsonify({'message': 'Oy başarıyla eklendi'}) 