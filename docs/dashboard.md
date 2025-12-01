# 📊 Dashboard Streamlit (exposure dbt)

Une fois les données ingérées et les modèles dbt exécutés, on peut explorer les marts via une application Streamlit.

## Lancer le dashboard

```bash
streamlit run apps/bi-streamlit/app.py
```

URL par défaut :
http://localhost:8501

Ce dashboard s'appuie principalement sur le modèle `fct_obs_hourly`.

## Exposure dbt associée

Le dashboard est déclaré comme **exposure dbt** (`weather_bi_streamlit`), permettant de :

* cibler uniquement les modèles qui l’alimentent :

    ```bash
    dbt ls -s +exposure:weather_bi_streamlit
    ```

* exécuter uniquement ce périmètre :

    ```bash
    dbt run -s +exposure:weather_bi_streamlit
    dbt test -s +exposure:weather_bi_streamlit
    ```