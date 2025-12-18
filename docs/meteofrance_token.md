
# 🔑 Obtenir une clé API Météo-France

1) Créer un compte sur le portail des API Météo-France 
   1) Ouvrir la page “Données Publiques – Paquet Observation” : https://portail-api.meteofrance.fr/web/fr/api/DonneesPubliquesPaquetObservation
   2) Cliquer sur **“Souscrire à l’API gratuitement”**  

2) Récupérer le token et le placer dans `.env` :

    ```bash
    METEOFRANCE_TOKEN=xxxxx
    DUCKDB_PATH=data/warehouse.duckdb
  ```