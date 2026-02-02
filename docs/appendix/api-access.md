# API Access (Météo-France)

Real data ingestion requires a Météo-France API token.

To obtain a token:

1) Create an account on the Météo‑France API portal  
   - Open the page “Public Data – Observation Package” :      https://portail-api.meteofrance.fr/web/fr/api/DonneesPubliquesPaquetObservation  
   
   - Click **“Subscribe to the API for free”**

2) Store the token locally as an environment variable in `.env`:

```
METEOFRANCE_TOKEN=...
```
