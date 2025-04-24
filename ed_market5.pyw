"""
    Gestion et Import
"""
import threading
import tkinter as tk
from market_database import insert_into_database, start_observer
from market_application import MarketApplication

if __name__ == "__main__":
    FILE_PATH = r"C:\Users\ecpel\Saved Games\Frontier Developments\Elite Dangerous\Market.json"
    DB_PATH = 'market.db'

    # Créez la fenêtre principale Tkinter
    root = tk.Tk()

    # Instanciez l'interface avec la classe MarketApplication
    app = MarketApplication(root)

    # Insérer dans la base une première fois
    try:
        insert_into_database(FILE_PATH, DB_PATH)
    except FileNotFoundError:
        print(f"{FILE_PATH} est introuvable. Veuillez vérifier le chemin.")

    # Créer et démarrer le thread pour l'observateur
    observer_thread = threading.Thread(target=start_observer, args=(FILE_PATH, DB_PATH))
    observer_thread.daemon = True  # Le thread s'arrêtera lorsque le programme principal se termine
    observer_thread.start()

    # Boucle principale
    root.mainloop()
