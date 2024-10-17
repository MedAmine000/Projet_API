# utils/database.py

import mysql.connector
import os
from mysql.connector import Error

class Database:
    def __init__(self):
        """Initialise la connexion à la base de données lors de la création de l'objet"""
        try:
            self.connection = mysql.connector.connect(
                host='mysql-transport.alwaysdata.net',
                user='transport',
                password='kiks2002',
                database='transport_db'
            )
            if self.connection.is_connected():
                print("Connexion réussie à la base de données MySQL")
        except Error as e:
            print(f"Erreur lors de la connexion à la base de données : {e}")
            self.connection = None

    def execute_query(self, query, params=None):
        """Exécuter une requête SQL (INSERT, UPDATE, DELETE)"""
        if self.connection is None:
            print("Connexion non disponible")
            return
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()  # Valider les modifications
            print("Requête exécutée avec succès")
        except Error as e:
            print(f"Erreur lors de l'exécution de la requête : {e}")
            self.connection.rollback()  # Annuler les modifications en cas d'erreur
        finally:
            cursor.close()  # Assurer la fermeture du curseur

    def fetch_all(self, query, params=None):
        """Exécuter une requête SELECT et retourner tous les résultats"""
        if self.connection is None:
            print("Connexion non disponible")
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()  # Récupérer tous les résultats
            return result
        except Error as e:
            print(f"Erreur lors de l'exécution de la requête : {e}")
            return []
        finally:
            cursor.close()  # Assurer la fermeture du curseur

    def close_connection(self):
        """Fermer la connexion à la base de données"""
        if self.connection and self.connection.is_connected():
            self.connection.close()  # Fermer la connexion
            print("Connexion MySQL fermée")
    