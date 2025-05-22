# database_chatbot_agent

File structure:
/project-root
│
├── main.py                      # FastAPI app
├── powerbi/                     # 💡 Dedicated Power BI logic
│   ├── auth.py                  # Handles Azure AD token fetching
│   └── query.py                 # Sends queries to Power BI API
├── .env                         # Your API keys and secrets
├── requirements.txt