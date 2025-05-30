from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routes import borrowers
from backend.database import init_db
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import threading
import time
import os
import sys


load_dotenv()

app = FastAPI(title="Liberia Microloan Risk Assessment Tool")

# Initialize database
init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(borrowers.router, prefix="/api/borrowers", tags=["Borrowers"])

# Serve static files (frontend)
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Scheduler function for periodic score updates
def update_scores_periodically():
    """
    Background task to periodically update borrower risk scores
    """
    def score_updater():
        while True:
            try:
                from backend.database import get_all_borrowers, connect_db
                from LLMs.scoring_engine import calculate_risk_score
                from LLMs.risk_classifier import classify_risk
                from Data.regional_data import load_regional_data, get_region_stats
                from application_layer.loan_decision_interface import approve_loan
                from application_layer.policy_settings import get_default_policy
                
                print("🔄 Running periodic score update...")
                
                # Load regional data
                try:
                    regional_data = load_regional_data("intelligence_layer/regional_data.json")
                except:
                    regional_data = {
                        "Montserrado": {"unemployment_rate": 0.12, "avg_income": 200},
                        "Bong": {"unemployment_rate": 0.18, "avg_income": 150},
                        "Nimba": {"unemployment_rate": 0.15, "avg_income": 180}
                    }
                
                # Get all borrowers
                borrowers = get_all_borrowers()
                policy = get_default_policy()
                
                # Update each borrower's score
                conn = connect_db()
                c = conn.cursor()
                
                for borrower in borrowers:
                    if borrower.get('base_score') is not None:
                        region_data = get_region_stats(borrower['region'], regional_data)
                        if not region_data:
                            region_data = {"unemployment_rate": 0.15, "avg_income": 175}
                        
                        # Recalculate risk score
                        new_score = calculate_risk_score(borrower, region_data)
                        new_risk = classify_risk(new_score)
                        
                        # Update decision
                        is_approved = approve_loan(new_risk, policy)
                        decision = "Approved" if is_approved else "Rejected"
                        if new_risk == "Medium" and is_approved:
                            decision = "Conditional"
                        
                        # Update database
                        c.execute("""
                            UPDATE borrowers SET adjusted_score=?, risk=?, decision=?
                            WHERE id=?
                        """, (new_score, new_risk, decision, borrower['id']))
                
                conn.commit()
                conn.close()
                print("✅ Score update completed successfully")
                
            except Exception as e:
                print(f"❌ Error in score update: {e}")
            
            # Wait 30 minutes before next update
            time.sleep(1800)
    
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=score_updater, daemon=True)
    scheduler_thread.start()
    print("🚀 Periodic score updater started")

# Start the scheduler
update_scores_periodically()

@app.get("/")
def root():
    """Root endpoint - serve frontend or API info"""
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    else:
        return {
            "message": "Liberia Microloan Risk Assessment Tool API",
            "status": "active",
            "endpoints": {
                "borrowers": "/api/borrowers",
                "docs": "/docs",
                "frontend": "Place HTML files in 'frontend' directory"
            }
        }

@app.get("/dashboard")
def dashboard():
    """Dashboard endpoint"""
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    else:
        from application_layer.dashboard import render_dashboard
        from backend.database import get_all_borrowers
        
        borrowers = get_all_borrowers()
        render_dashboard(borrowers)
        return {"message": "Dashboard rendered in console"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "intelligence_layer": "active",
        "application_layer": "active"
    }