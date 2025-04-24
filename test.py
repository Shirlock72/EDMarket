import tkinter as tk
from tkinter import ttk
import sqlite3
import locale

class GestionFenetre:
    def __init__(self, root):
        self.root = root
        self.root.title("Saisie des Quantités")
        self._creer_base_donnees()
        self._creer_widgets()
        self._charger_donnees()
        self._charger_categories()
        self._mettre_a_jour_marchandises(' ')

    def _creer_base_donnees(self):
        # Création ou connexion à la base de données SQLite
        self.connexion = sqlite3.connect("market.db")
        self.curseur = self.connexion.cursor()
        self.connexion.commit()

    def _creer_widgets(self):
        # Champ Personnel
        tk.Label(self.root, text="Personnel :").grid(row=0, column=0, sticky="w")
        self.champ_personnel = tk.StringVar()
        tk.Entry(self.root, textvariable=self.champ_personnel).grid(row=0, column=1, sticky="w")
        
        # Liste déroulante pour les catégories
        tk.Label(self.root, text="Catégorie :").grid(row=1, column=0, sticky="w")
        self.liste_categories = ttk.Combobox(self.root, state="readonly")
        self.liste_categories.grid(row=1, column=1, sticky="w")
        self.liste_categories.bind("<<ComboboxSelected>>", self._mettre_a_jour_marchandises)
        
        # Liste déroulante pour les marchandises
        tk.Label(self.root, text="Marchandise :").grid(row=2, column=0, sticky="w")
        self.liste_marchandises = ttk.Combobox(self.root)
        self.liste_marchandises.grid(row=2, column=1, sticky="w")

        # Champ Quantité
        tk.Label(self.root, text="Quantité :").grid(row=3, column=0, sticky="w")
        self.champ_quantite = tk.StringVar()
        tk.Entry(self.root, textvariable=self.champ_quantite).grid(row=3, column=1, sticky="w")

        results_frame = tk.Frame(self.root)
        results_frame.grid(row=7,
                           column=0,
                           columnspan=6,
                           padx=10,
                           pady=10,
                           sticky="nsew")

        # Tableau pour afficher les données
        colonnes = ("Marchandise", "Quantité", "Personnel")
        self.table = ttk.Treeview(results_frame, columns=colonnes, show="headings", selectmode="browse")
        for col in colonnes:
            self.table.heading(col, text=col)
        self.table.grid(row=4, column=0, columnspan=3)
        # Associer un événement pour sélectionner une ligne
        self.table.bind("<<TreeviewSelect>>", self.selectionner_ligne)

        self.table.pack(side="left", fill="both", expand=True)  # Étendre le tableau

        # Scrollbar pour le tableau
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical",
                                  command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)

        # Configuration pour rendre le tableau redimensionnable
        self.root.grid_rowconfigure(7, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


        # Bouton pour supprimer la ligne sélectionnée
        tk.Button(self.root, text="Supprimer la sélection", command=self.supprimer_ligne).grid(row=1, column=2)

        # Associer la touche "Entrée" au bouton par défaut
        self.root.bind('<Return>', self.enregistrer_donnees)

    def enregistrer_donnees(self, _):
        # Récupérer les données saisies
        personnel_value = self.champ_personnel.get()
        marchandise_value = self.liste_marchandises.get()
        quantite_value = self.champ_quantite.get()

        # Sauvegarder dans la base SQLite
        self.curseur.execute("delete from need_items where id = ? and label = ?", (marchandise_value, personnel_value))
        self.connexion.commit()
        self.curseur.execute("""
            INSERT INTO need_items (id, need, label)
            VALUES (?, ?, ?)
        """, (marchandise_value, quantite_value, personnel_value))
        self.connexion.commit()

        # Ajouter dans le tableau
        self._charger_donnees()

        self.liste_marchandises.set("- Aucun -")  # Marchandise
        self.liste_categories.set("- Aucun -")
        self.champ_quantite.set("")  # Quantité
        self.champ_personnel.set("")  # Personnel

    def _charger_donnees(self):
        # Effacer les données existantes dans le tableau
        self.table.delete(*self.table.get_children())

        # Charger les données depuis la base SQLite dans le tableau
        self.curseur.execute("SELECT id, need, label FROM need_items order by label, id")
        for row in self.curseur.fetchall():
            # Convertir le tuple en liste pour le modifier
            row_list = list(row)
            
            # S'assurer que la locale est définie
            import locale
            locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
            
            # Appliquer le format uniquement si la quantité est un nombre
            if isinstance(row_list[1], int) or str(row_list[1]).isdigit():
                row_list[1] = locale.format_string("%d", int(row_list[1]), grouping=True)
            # Insérer les données modifiées dans la table Treeview
            self.table.insert("", "end", values=row_list)
        self.table.column("Quantité", anchor="center")

    def supprimer_ligne(self):
        # Récupérer l'élément sélectionné
        selection = self.table.selection()
        if selection:
            # Supprimer de la base SQLite
            item = selection[0]
            valeurs = self.table.item(item, "values")
            self.curseur.execute("""
                DELETE FROM need_items
                WHERE id = ? AND need = ? AND label = ?
            """, valeurs)
            self.connexion.commit()

            # Supprimer de la table Treeview
            self.table.delete(item)

    def __del__(self):
        # Fermer la connexion à la base de données lors de la destruction de l'objet
        self.connexion.close()
    
    def _charger_categories(self):
        # Charger les catégories distinctes depuis la base de données
        self.curseur.execute("SELECT DISTINCT category FROM market_items order by category")
        categories = ["- Aucun -"] + [row[0] for row in self.curseur.fetchall()]
        self.liste_categories["values"] = categories
        self.liste_categories.set(categories[0])

    def _mettre_a_jour_marchandises(self, event):
        # Mettre à jour la liste des IDs en fonction de la catégorie sélectionnée
        categorie_selectionnee = self.liste_categories.get()
        self.curseur.execute("SELECT distinct name FROM market_items WHERE category = ? order by name", (categorie_selectionnee,))
        ids = ["- Aucun -"] + [row[0] for row in self.curseur.fetchall()]
        self.liste_marchandises["values"] = ids
        self.liste_marchandises.set(ids[0])

    def selectionner_ligne(self, event):
        # Récupérer la ligne sélectionnée
        for item in self.table.selection():
            valeurs = self.table.item(item, "values")
            # Remplir les champs avec les valeurs sélectionnées
            self.liste_marchandises.set(valeurs[0])  # Marchandise
            self.champ_quantite.set(valeurs[1])  # Quantité
            self.champ_personnel.set(valeurs[2])  # Personnel
            # Positionner le curseur sur le champ Quantité
        self.root.focus_set()  # S'assurer que la fenêtre principale a le focus
        # Positionner le curseur sur le champ Quantité
        for widget in self.root.grid_slaves():
            if isinstance(widget, tk.Entry) and widget.cget("textvariable") == str(self.champ_quantite):
                widget.focus_set()
                widget.selection_range(0, tk.END)

# Exécution de la fenêtre principale
if __name__ == "__main__":
    fenetre = tk.Tk()
    app = GestionFenetre(fenetre)
    fenetre.mainloop()