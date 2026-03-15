# Smart Agri App

## Files to send
- `agri1.py`
- `modules/`
- `smart_agri.db`
- `requirements.txt`
- `README.md`
- `.env.example`
- `.streamlit/secrets.toml.example`

## Setup
```powershell
python -m pip install -r requirements.txt
streamlit run agri1.py
```

## API configuration
The app works without API keys using fallback data, but live services are enabled when you configure these values.

Option 1: local `.env`
```powershell
Copy-Item .env.example .env
```

Option 2: Streamlit secrets
Create `.streamlit/secrets.toml` from `.streamlit/secrets.toml.example`.

For live weather data:
- `OPENWEATHERMAP_API_KEY`

For live mandi data:
- `DATA_GOV_API_KEY`
- `MANDI_RESOURCE_ID`

## Notes
- Do not include `.venv/` in the zip.
- If you later add trained disease model files, include a `models/` folder.
- The sidebar shows whether weather and mandi services are running in `Live` or `Fallback` mode.
