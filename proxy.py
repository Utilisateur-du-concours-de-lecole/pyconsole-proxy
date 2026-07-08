from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_CALO_API_KEYS")
if not GEMINI_API_KEY:
    print("❌ Erreur : La clé API n'est pas dans le fichier .env")
    print("   Assure-toi que GEMINI_CALO_API_KEYS est défini")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

@app.post("/debug")
async def debug_code(request: CodeRequest):
    try:
        prompt = "Analyse ce code Python et donne-moi :\n"
        prompt += "1. Les erreurs (s'il y en a)\n"
        prompt += "2. Des suggestions d'amélioration\n"
        prompt += "3. Une version corrigée si nécessaire\n\n"
        prompt += "Code :\n"
        prompt += "```python\n"
        prompt += request.code + "\n"
        prompt += "```\n\n"
        prompt += "Réponds en français, de manière pédagogique et encourageante.\n"
        prompt += "Si le code est parfait, félicite l'utilisateur et donne des conseils pour aller plus loin."

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}",
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Erreur API Gemini: {response.status_code} - {response.text}"
                }
            
            data = response.json()
            return {
                "success": True,
                "analysis": data["candidates"][0]["content"]["parts"][0]["text"]
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/")
async def root():
    return {"message": "Proxy Gemini fonctionne !"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
