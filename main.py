from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
LABEL_FILTER = "bug"  # Change this to your label

@app.post("/github-webhook")
async def github_webhook(request: Request):
    try:
        payload = await request.json()

        # Handle ping event
        if "zen" in payload:
            return JSONResponse(content={"msg": "pong"}, status_code=200)

        action = payload.get("action")
        issue = payload.get("issue")

        if action and issue:
            labels = [label["name"] for label in issue.get("labels", [])]
            if LABEL_FILTER in labels:
                async with httpx.AsyncClient() as client:
                    await client.post(DISCORD_WEBHOOK_URL, json={ # type: ignore
                        "content": f"📝 New issue with `{LABEL_FILTER}` label:\n"
                                   f"**{issue['title']}**\n{issue['html_url']}"
                    })

        return JSONResponse(content={"status": "ok"}, status_code=200)

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=200)
