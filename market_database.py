"""
    Import du fichier json
"""
import json
import sqlite3
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def insert_into_database(file_path, db_path='market.db'):
    """Insère les données du fichier JSON dans la base SQLite."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    star_system = data.get("StarSystem", "Inconnu")
    station_name = data.get("StationName", "Inconnu")
    timestamp = data.get("timestamp", "Inconnu")

    cursor.execute('DELETE FROM market_items WHERE star_system = ? AND station_name = ?',
                   (star_system, station_name))

    for item in data["Items"]:
        cursor.execute('''
            INSERT INTO market_items (
                id, name, category, buy_price, sell_price, mean_price,
                stock, demand, star_system, station_name, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get("id"),
            item.get("Name_Localised"),
            item.get("Category_Localised"),
            item.get("BuyPrice"),
            item.get("SellPrice"),
            item.get("MeanPrice"),
            item.get("Stock"),
            item.get("Demand"),
            star_system,
            station_name,
            timestamp
        ))

    conn.commit()
    conn.close()

    print("Données insérées avec succès dans la base SQLite!")

def is_file_stable(file_path, wait_time=1, attempts=5):
    """Vérifie si un fichier est stable (pas en cours de modification)."""
    previous_size = -1
    for _ in range(attempts):
        current_size = os.path.getsize(file_path)
        if current_size == previous_size:
            return True
        previous_size = current_size
        time.sleep(wait_time)
    return False

class MarketFileHandler(FileSystemEventHandler):
    """Handler pour détecter les modifications d'un fichier spécifique."""
    def __init__(self, file_path, db_path='market.db'):
        self.file_path = file_path
        self.db_path = db_path

    def on_modified(self, event):
        """
            A chaque modification du fichier
        Args:
            event (event): Nature de l'événement
        """
        if event.src_path.endswith("Market.json"):
            print("Modification détectée, vérification de la stabilité du fichier...")
            if is_file_stable(self.file_path):
                print("Fichier stable, mise à jour de la base de données...")
                insert_into_database(self.file_path, self.db_path)
            else:
                print("Le fichier est toujours en cours de modification.")

def start_observer(file_path, db_path):
    """
        Démarrage de la surveillance
    Args:
        file_path (string): Emplacement du fichier à surveiller
        db_path (string): Emplacement de la base de données
    """
    event_handler = MarketFileHandler(file_path, db_path)
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(file_path), recursive=False)
    print("Surveillance du fichier activée...")

    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
