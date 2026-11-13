import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from database import init_db, save_lead, get_all_leads, log_campaign, get_all_campaigns
from agent import generate_agent_response

app = FastAPI(title="Omnichannel AI Marketing Agent")

# Mount frontend static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

init_db()

@app.get("/")
def serve_dashboard():
    return FileResponse("static/frontend.html")

# INBOUND DATA SCHEMAS
class GenericLeadRequest(BaseModel):
    source: str          # indiamart, gmail, instagram, facebook, youtube, website
    name: str
    contact: str
    query: str

class BulkCampaignRequest(BaseModel):
    channel: str         # whatsapp, sms, email
    recipients: list[str]
    template_message: str

#  INGESTION / WEBHOOKS
@app.post("/api/webhook/ingest")
def ingest_lead(data: GenericLeadRequest):
    """Universal Webhook handler for IndiaMART, FB, IG, Gmail, YouTube, Website leads"""
    result = generate_agent_response(data.source, data.name, data.query)
    
    save_lead(
        source=data.source,
        name=data.name,
        contact=data.contact,
        query=data.query,
        ai_reply=result["reply"],
        landing_url=result["landing_url"]
    )
    return {
        "status": "success",
        "message": f"Processed inbound event from {data.source}",
        "ai_response": result["reply"],
        "landing_url": result["landing_url"]
    }

#  CAMPAIGNS / BROADCAST 
@app.post("/api/campaigns/broadcast")
def run_broadcast(data: BulkCampaignRequest):
    """Bulk sender for WhatsApp, SMS, and Email campaigns"""
    sent_count = 0
    for recipient in data.recipients:
        # Simulate outbound API dispatch (WhatsApp Cloud API / Twilio / Brevo)
        log_campaign(data.channel, recipient.strip(), data.template_message, "Delivered")
        sent_count += 1

    return {"status": "success", "channel": data.channel, "dispatched": sent_count}

# DASHBOARD METRICS API 
@app.get("/api/leads")
def fetch_leads():
    return get_all_leads()

@app.get("/api/campaigns")
def fetch_campaigns():
    return get_all_campaigns()

@app.get("/api/stats")
def fetch_stats():
    leads = get_all_leads()
    campaigns = get_all_campaigns()
    return {
        "total_leads": len(leads),
        "total_broadcasts": len(campaigns),
        "sources": {
            "indiamart": len([l for l in leads if l["source"] == "indiamart"]),
            "gmail": len([l for l in leads if l["source"] == "gmail"]),
            "instagram": len([l for l in leads if l["source"] == "instagram"]),
            "facebook": len([l for l in leads if l["source"] == "facebook"]),
            "youtube": len([l for l in leads if l["source"] == "youtube"]),
            "website": len([l for l in leads if l["source"] == "website"]),
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
