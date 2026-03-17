# VotexChain ⛓️🗳️

**VotexChain** is a distributed blockchain-based election monitoring system built in Python. It provides a transparent, tamper-proof, and verifiable infrastructure for tracking votes across polling stations using Proof-of-Work consensus, smart contracts, and a peer-to-peer network.

---

## ✨ Features

- 🔗 **Blockchain Ledger** — Immutable vote records secured with SHA-256 hashing and Proof-of-Work
- 📡 **Peer-to-Peer Network** — Multi-threaded socket-based distributed node architecture
- 📜 **Smart Contracts** — Rule enforcement for election validity (minimum observers, double-vote prevention, ballot box quotas)
- 👁️ **Observer System** — Cryptographically signed vote verifications with full audit trails
- 🚫 **Double-Vote Prevention** — Global voter registry checked across the entire blockchain
- 🗄️ **PostgreSQL Persistence** — Blocks and transactions stored via SQLAlchemy ORM
- 🌐 **REST API** — Flask endpoint for programmatic vote submission
- 🖥️ **GUI & CLI** — Tkinter-based graphical interface and a menu-driven CLI

---

## 🏗️ Architecture

```
Observer Input ──► Smart Contract Validation ──► Pending Transactions
                                                          │
                                                   Mine Block (PoW)
                                                          │
                                             Broadcast to P2P Network
                                                          │
                                              Peers Validate & Sync
                                                          │
                                             PostgreSQL Persistence
```

---

## 📂 Project Structure

```
VotexChain/
├── Blockchain.py        # Core blockchain, PoW mining, chain validation
├── Network.py           # P2P node, peer discovery, message broadcasting
├── SmartContract.py     # Election rules engine and state management
├── Observer.py          # Vote signing, verification, and audit reports
├── models.py            # SQLAlchemy ORM models (Block, Transaction)
├── database.py          # Database connection and session management
├── init_db.py           # Database initialization script
├── app.py               # Flask REST API (POST /add_vote)
├── gui.py               # Tkinter GUI for observers
├── main.py              # CLI menu interface
└── requirements.txt     # Python dependencies
```

---

## ⚙️ Installation

### Requirements
- Python 3.9+
- PostgreSQL

### Setup

```bash
# Clone the repository
git clone https://github.com/MehmetPekerr/VotexChain.git
cd VotexChain

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py
```

---

## 🚀 Usage

### Graphical Interface (GUI)
```bash
python gui.py
```

### Command-Line Interface (CLI)
```bash
python main.py
```

### REST API Server
```bash
python app.py
```

**Submit a vote via API:**
```bash
curl -X POST http://localhost:5000/add_vote \
  -H "Content-Type: application/json" \
  -d '{"observer_id": "OBS001", "voter_id": "V123", "ballot_box": "BB01"}'
```

---

## 🔧 Smart Contract Rules

| Rule | Description |
|------|-------------|
| `can_start_election()` | Requires at least 3 registered observers |
| `can_vote()` | Voter must be registered, not voted, and use a valid ballot box |
| `can_add_ballot_box()` | Only allowed during an active election |
| `can_add_observer()` | Prevents duplicate observer registrations |
| `validate_vote()` | Cross-checks voter and ballot box legitimacy |
| `validate_ballot_box()` | Vote count cannot exceed registered voter total |
| `validate_party_votes()` | Party vote totals must match overall count |

---

## 📡 Network Protocol

Nodes communicate via TCP sockets using 4 message types:

| Message | Description |
|---------|-------------|
| `new_block` | Broadcasts a freshly mined block to all peers |
| `new_transaction` | Shares a pending transaction across the network |
| `sync_request` | Requests full blockchain synchronization from a peer |
| `peer_list` | Shares known peer addresses for discovery |

---

## 🗃️ Database Schema

```
Block
├── id (PK)
├── index
├── hash
├── previous_hash
├── timestamp
├── data (JSON)
└── nonce

Transaction
├── id (PK)
├── block_id (FK → Block)
├── sender
├── recipient
└── amount
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3 |
| Blockchain | Custom PoW implementation |
| Networking | Python `socket` + `threading` |
| Smart Contracts | Custom rules engine |
| Database | PostgreSQL + SQLAlchemy |
| API | Flask |
| GUI | Tkinter |
| Hashing | SHA-256 (hashlib) |

---

## 📋 Requirements

```
psycopg2-binary==2.9.9
SQLAlchemy==2.0.27
Flask
```

---

## 🔒 Security Properties

- **Immutability**: Any block modification invalidates all subsequent hashes
- **Double-vote protection**: Voter IDs tracked globally across the full chain
- **Observer accountability**: Every verified vote carries a cryptographic observer signature
- **Distributed trust**: No single point of failure — any peer can validate the full chain

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">
  Built with ⛓️ by <a href="https://github.com/MehmetPekerr">MehmetPekerr</a>
</div>

<!-- Maintenance: metadata refresh commit for repository insights recalculation. -->
