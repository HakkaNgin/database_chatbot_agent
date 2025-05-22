from .auth_powerBI import get_access_token
import httpx

async def ask_powerbi(question: str):
    token = await get_access_token()
    # TODO: Transform question → DAX/REST query and send it to Power BI API
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.powerbi.com/...endpoint...", headers=headers)
        return response.json()
