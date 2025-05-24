# 🧠 database_chatbot_agent

A FastAPI-based chatbot that converts natural language queries into SQL to retrieve insights from a Google BigQuery dataset and respond intelligently via OpenAI's GPT API.

---

## 📁 File Structure

```
/project-root
│
├── main.py                      # FastAPI app entry point
├── powerbi/                     # 💡 (Optional) Power BI integration logic
│   ├── auth.py                  # Handles Azure AD token fetching
│   └── query.py                 # Sends queries to Power BI API
├── .env                         # Stores API keys and secrets (do not commit)
├── requirements.txt             # Python dependencies
└── static/                      # Frontend HTML interface
```

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/database_chatbot_agent.git
cd database_chatbot_agent
```

---

### 2. Create Azure Web App
- Go to the [Azure portal](https://portal.azure.com/#home)
- Navigate to **App Services** → **Create**
- Select:
  - **Operating System**: Linux  
  - **Runtime Stack**: Python 3.11
- Fill in the rest of the fields and create the app
- After creation, you’ll see your app listed under App Services

---

### 3. Configure OpenAI
- [Create an OpenAI account](https://platform.openai.com/docs/overview)
- [Add API credits](https://platform.openai.com/settings/organization/billing/overview)  
  (see [pricing here](https://openai.com/api/pricing))
- Go to [API Keys](https://platform.openai.com/account/api-keys) and create a new secret key
- On your Azure app:
  - Go to **Settings → Configuration → Environment Variables**
  - Add:
    ```
    Name: OPENAI_API_KEY
    Value: <your-openai-secret-key>
    ```

---

### 4. Prepare Google BigQuery Dataset
- Go to [Google Cloud Console](https://console.cloud.google.com/welcome)
- Open **BigQuery** from the top search bar
- Click **+ Add Data** and upload or connect your dataset (CSV or public)

📝 Make sure to note your full table path:  
`project_id.dataset_name.table_name`

---

### 5. Configure BigQuery API and Credentials
- [Create a new GCP project](https://console.cloud.google.com/projectselector2/home/dashboard)
- [Enable the BigQuery API](https://console.cloud.google.com/apis/library/bigquery.googleapis.com)
- [Create a service account](https://console.cloud.google.com/iam-admin/serviceaccounts)
  - Assign roles:
    - `BigQuery Data Viewer`
    - `BigQuery Job User`
    - (Optional) `BigQuery Admin`
- Generate a **JSON key** file
- On Azure:
  - Go to **Settings → Configuration**
  - Add a new variable:
    ```
    Name: GOOGLE_APPLICATION_CREDENTIALS_JSON
    Value: <paste the contents of the JSON file>
    ```

---

### 6. Deploy via GitHub Actions
- On GitHub:
  - Go to **Settings → Actions → General**
  - Set: **Allow all actions and reusable workflows**
- On Azure:
  - Go to your app → **Deployment Center**
  - Source: `GitHub`
  - Select:
    - Organisation
    - Repository
    - Branch
  - Enable **Continuous Deployment**

🔁 This allows your FastAPI app to be rebuilt and deployed on each GitHub commit.

📽️ [Watch deployment tutorial](https://www.youtube.com/watch?v=Rp-TMHrwCn4)

---

### 7. Access Your Application
- Go to **App Service → Overview**
- Click **Browse** or copy the **URL** field

---

### 8. Debugging Logs
- Azure Portal → App → **Logs** → **Log stream**

---

## ✅ Checklist Before Deployment

- [ ] Update `.env` or Azure env variables for OpenAI and BigQuery
- [ ] Ensure your `requirements.txt` is up-to-date
- [ ] Confirm the full table path is in your GPT SQL generation prompt
- [ ] Static files (HTML UI) are located in the `/static` folder
- [ ] Test locally with:
  ```bash
  uvicorn main:app --reload
  ```

---
