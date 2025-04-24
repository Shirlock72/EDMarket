"""
Création de l'application
"""
import sqlite3
import locale
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, UTC

class MarketApplication:
    """
    Création de l'inteface graphique
    """
    def __init__(self, rt):
        """
        Initialise l'interface graphique.
        :param root: la fenêtre principale (Tk)
        """
        self.root = rt
        self.root.title("EDMarket - @Shirlock")
        self.root.geometry("1280x1024")
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')  # Example: French locale
        self.fields_and_comboboxes = []
        self.rows = []

        # Appel de la méthode pour créer les widgets
        # Conteneur des comboboxes
        self.criteria_frame = tk.Frame(self.root)
        self.criteria_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.star_system_combobox = ttk.Combobox(self.criteria_frame, values=[""],
                                                 font=("Calibri", 11))
        self.station_name_combobox = ttk.Combobox(self.criteria_frame, values=[""],
                                                  font=("Calibri", 11))
        self.category_combobox = ttk.Combobox(self.criteria_frame, values=[""],
                                              font=("Calibri", 11))
        self.name_combobox = ttk.Combobox(self.criteria_frame, values=[""], font=("Calibri", 11))
        self.stock_var = tk.BooleanVar()
        self.demand_var = tk.BooleanVar()
        self.stock_checkbox = tk.Checkbutton(self.criteria_frame, text="Stock > 0",
                                             variable=self.stock_var,
                                             font=("Calibri", 11), command=self.search)
        self.demand_checkbox = tk.Checkbutton(self.criteria_frame,
                                              text="Demande > 0",
                                              variable=self.demand_var,
                                              font=("Calibri", 11), command=self.search)
        self.search_button = tk.Button(self.criteria_frame,
                                       text="Rechercher",
                                       font=("Calibri", 11), command=self.search)

        # Création des listes déroulantes
        self.liste_deroulante()

        # tableau des critère de recherche
        self.ajout_critere()

        # Définition de la table
        self.definition_table()

        # Connexion pour charger les valeurs des champs dans les ComboBoxes
        self.conn = sqlite3.connect("market.db")
        self.cursor = self.conn.cursor()

        # chargement des listes déroulantes
        self.chargement_liste_deroulante()


    def liste_deroulante(self):
        """
        Définition des listes de sélections
        """
        # Ligne 1
        tk.Label(self.criteria_frame,
                 text="Système Stellaire :",
                 font=("Calibri", 11)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self.criteria_frame,
                 text="Nom de la Station :",
                 font=("Calibri", 11)).grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.star_system_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.station_name_combobox.grid(row=1, column=3, padx=10, pady=5, sticky="w")

        # Ligne 2
        tk.Label(self.criteria_frame,
                 text="Catégorie :",
                 font=("Calibri", 11)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self.criteria_frame,
                 text="Marchandise :",
                 font=("Calibri", 11)).grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.category_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.name_combobox.grid(row=2, column=3, padx=10, pady=5, sticky="w")

        # Ligne 5
        self.stock_checkbox.grid(row=5, column=0, padx=10, columnspan=3, pady=5, sticky="w")
        self.demand_checkbox.grid(row=5, column=1, padx=10, columnspan=3, pady=5, sticky="w")

        # Ligne 6
        self.search_button.grid(row=6, column=0, columnspan=6, pady=20, sticky="w")

        # Associer la touche "Entrée" au bouton par défaut
        self.root.bind('<Return>', self.search)

        self.star_system_combobox.bind('<<ComboboxSelected>>', self.update_station)
        self.station_name_combobox.bind('<<ComboboxSelected>>',
                                        lambda event: self.search_button.invoke())
        self.category_combobox.bind('<<ComboboxSelected>>', self.update_marchandise)
        self.name_combobox.bind('<<ComboboxSelected>>',
                                lambda event: self.search_button.invoke())
        self.stock_checkbox.bind('<<ComboboxSelected>>',
                                 lambda event: self.search_button.invoke())
        self.demand_checkbox.bind('<<ComboboxSelected>>',
                                  lambda event: self.search_button.invoke())

    def update_marchandise(self, _):
        """
            Mise à jour de l'affichage
        Args:
            _ (event): non utilisé
        """
        category = self.category_combobox.get()
        if category == '- Aucun -':
            req = "SELECT DISTINCT name FROM market_items ORDER BY name"
        else:
            req = "SELECT DISTINCT name FROM market_items"\
                f" where category = '{category}' ORDER BY name"
        self.cursor.execute(req)
        self.name_combobox["values"] = []
        values = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
        self.name_combobox["values"] = ["- Aucun -"] + values
        self.name_combobox.set("- Aucun -")
        self.search()

    def update_station(self, _):
        """
            Mise à jour des stations au changement de système

        Args:
            _ (event): non utilisé
        """
        star_system = self.star_system_combobox.get()
        if star_system == '- Aucun -':
            req = "SELECT DISTINCT name FROM market_items ORDER BY name"
        else:
            req = "SELECT DISTINCT station_name FROM market_items"\
            f" where star_system = '{star_system}' ORDER BY station_name"
        self.cursor.execute(req)
        self.station_name_combobox["values"] = []
        values = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
        self.station_name_combobox["values"] = ["- Aucun -"] + values
        self.station_name_combobox.set("- Aucun -")
        self.search()

    def ajout_critere(self):
        """
        Définition des critères de recherche
        """
        # Tableau des critères de recherche
        self.fields_and_comboboxes.append(("star_system",
                                           self.star_system_combobox, "Système stellaire"))
        self.fields_and_comboboxes.append(("station_name", self.station_name_combobox, "Station"))
        self.fields_and_comboboxes.append(("category", self.category_combobox, "Catégorie"))
        self.fields_and_comboboxes.append(("name", self.name_combobox, "Marchandise"))
        self.fields_and_comboboxes.append(("stock", "", "Stock"))
        self.fields_and_comboboxes.append(("sell_price", "", "Prix Vente"))
        self.fields_and_comboboxes.append(("demand", "", "Demande"))
        self.fields_and_comboboxes.append(("buy_price", "", "Prix Achat"))
        self.fields_and_comboboxes.append(("mean_price", "", "Prix Moyen"))
        self.fields_and_comboboxes.append(("id", "", "ID"))
        self.fields_and_comboboxes.append(("timestamp", "", "Horodatage"))

    def chargement_liste_deroulante(self):
        """
        Charger les valeurs disponibles pour chaque champ dans les ComboBoxes
        """
        for field, combobox, _ in self.fields_and_comboboxes:
            if combobox != "":
                self.cursor.execute(f"SELECT DISTINCT {field} FROM market_items ORDER BY {field}")
                values = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
                combobox["values"] = ["- Aucun -"] + values
                combobox.set("- Aucun -")

    def definition_table(self):
        """
        Tableau pour afficher les résultats
        """
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Calibri", 11, "bold"))

        results_frame = tk.Frame(self.root)
        results_frame.grid(row=7,
                           column=0,
                           columnspan=6,
                           padx=10,
                           pady=10,
                           sticky="nsew")

        self.results_table = ttk.Treeview(
            results_frame,
            style="Treeview",
            columns=[field for field, _, fr in self.fields_and_comboboxes if field != "id"],
            show="headings"
        )

        for field, _, field_fr in self.fields_and_comboboxes:
            if field != "id":  # Exclure la colonne 'id' de l'affichage
                self.results_table.heading(field, text=field_fr)
                if field in ["stock", "buy_price", "demand", "sell_price", "mean_price"]:
                    self.results_table.column(field, width=100, anchor="e")  # Alignement à droite
                else:
                    self.results_table.column(field, width=100, anchor="center")

        self.results_table.pack(side="left", fill="both", expand=True)  # Étendre le tableau

        # Scrollbar pour le tableau
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical",
                                  command=self.results_table.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_table.configure(yscrollcommand=scrollbar.set)

        # Configuration pour rendre le tableau redimensionnable
        self.root.grid_rowconfigure(7, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


    def search(self):
        """
        Effectue la recherche en fonction des critères définis 
        dans les ComboBoxes et des interrupteurs.
        """
        criteria = {
            "name": self.name_combobox.get(),
            "category": self.category_combobox.get(),
            "star_system": self.star_system_combobox.get(),
            "station_name": self.station_name_combobox.get(),
        }
        criteria = {key: value for key,
                    value in criteria.items() if value not in (None, "- Aucun -")}
        stock_filter = self.stock_var.get()
        demand_filter = self.demand_var.get()
        self.rows = self.query_database(criteria, stock_filter, demand_filter)

        self.display_results()

    def query_database(self, criteria, stock_filter, demand_filter):
        """Exécute une requête sur la base SQLite en fonction des critères et des interrupteurs."""
        try:

            # Construire la requête SQL dynamique en fonction des critères et des filtres
            query = "SELECT star_system, station_name, category, name, stock,"\
                " buy_price, demand, sell_price, mean_price, id, timestamp"\
                " FROM market_items WHERE 1=1"
            params = []
            for field, value in criteria.items():
                if value:  # Si un critère est spécifié
                    query += f" AND {field} LIKE ?"
                    params.append(f"%{value}%")

            # Ajouter les filtres pour stock > 0 et demand > 0
            if stock_filter:
                query += " AND stock > 0"
            if demand_filter:
                query += " AND demand > 0"
            query += " order by category, name, star_system, station_name"

            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'accès à la base de données : {e}")
            return []

    def display_results(self):
        """Affiche les résultats dans la table avec formatage et coloration."""

        # Supprimer les lignes existantes
        for row in self.results_table.get_children():
            self.results_table.delete(row)

        # Insérer les nouvelles lignes
        for row in self.rows:
            formatted_row = self.format_row(row)  # Modifier format_row pour retourner des styles

            # Insérer la ligne avec les tags nécessaires
            self.results_table.insert("", "end", values=formatted_row)

        # Ajuster les colonnes automatiquement après insertion des données
        self.adjust_columns()

    def adjust_columns(self):
        """
        Ajuste automatiquement la largeur des colonnes textuelles 
        et utilise les libellés pour les colonnes numériques.
        """
        # Liste des colonnes numériques
        numeric_columns = ["stock", "buy_price", "sell_price", "demand", "mean_price", "timestamp"]

        for col_index, col in enumerate(self.results_table["columns"]):
            # Récupérer la largeur du libellé de la colonne
            column_heading = self.results_table.heading(col)["text"]
            max_width = len(column_heading)  # Largeur du libellé par défaut

            # Si ce n'est pas une colonne numérique, ajuster en fonction des données
            if col not in numeric_columns:
                for row in self.rows:
                    cell_value = str(row[col_index])  # Convertir en chaîne de caractères
                    max_width = max(max_width, len(cell_value))

            # Ajuster la largeur avec un petit padding
            if col in numeric_columns:
                self.results_table.column(col, width=max_width * 10)
            else:
                self.results_table.column(col, width=max_width * 7, anchor="w")

    def format_row(self, row):
        """
        Formatage des colonnes
        Args:
            row (champ): un champ

        Returns:
            Champ: Champ formatté
        """
        formatted_row = []

        for i, value in enumerate(row):
            if i == 9:
                continue
            elif i == 10: # Colonne `timestamp`
                # Date de référence
                date_reference = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                # Ajout du fuseau horaire UTC à date_reference
                date_reference = date_reference.replace(tzinfo=UTC)

                # Date actuelle (remplaçable par une autre date si nécessaire)
                date_actuelle = datetime.now(UTC)

                # Calcul de la différence
                difference = date_actuelle - date_reference

                # Analyse de la différence
                if difference.days > 1:
                    dif = f"Il y a {difference.days} jours"
                elif difference.seconds >= 3600:  # Une heure = 3600 secondes
                    heures = difference.seconds // 3600
                    dif = f"Il y a {heures} heures"
                else:
                    minutes = difference.seconds // 60
                    dif = f"Il y a {minutes} minutes"

                formatted_row.append(dif)
            elif i >= 4:  # Colonnes numériques
                formatted_value = locale.format_string("%d", value, grouping=True)
                if i == 5 :
                    if row[5] < row[8] * 0.75:
                        formatted_value = formatted_value + " \U0001F600"
                    elif row[5] > row[8]:
                        formatted_value = formatted_value + " \U0001F480"
                    formatted_value = formatted_value + "  (" + str(row[5] - row[8]) + ")"
                if i == 7:
                    formatted_value = formatted_value + "  (" + str(row[7] - row[8]) + ")"
                formatted_row.append(formatted_value)
            else:
                formatted_row.append(value)

        return formatted_row

if __name__ == "__main__":
    # Créez la fenêtre principale Tkinter
    root = tk.Tk()

    # Instanciez l'interface avec la classe MarketApplication
    app = MarketApplication(root)

    # Boucle principale
    root.mainloop()
