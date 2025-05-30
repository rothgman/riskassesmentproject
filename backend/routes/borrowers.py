from backend.database import get_all_borrowers, connect_db
import requests
from fastapi import APIRouter, HTTPException
from LLMs.scoring_engine import calculate_risk_score
from LLMs.risk_classifier import classify_risk
from Data.regional_data import load_regional_data, get_region_stats
from LLMs.llm_inferace import get_llm_response
from LLMs.explainability import generate_explanation
from application_layer.loan_decision_interface import approve_loan
from application_layer.policy_settings import get_default_policy
from pydantic import BaseModel
import os
import uuid
import sys

# Define the BorrowerInput model
class BorrowerInput(BaseModel):
    name: str
    region: str
    loan_amount: float
    repayment_rate: float = 0.9

class ExplainInput(BaseModel):
    id: str
    name: str
    region: str
    loan_amount: float
    repayment_rate: float = 0.9

router = APIRouter()

# Load regional data once at startup
try:
    REGIONAL_DATA = load_regional_data("Data/regional_data.json")
except:
    # Fallback data if file not found
    REGIONAL_DATA = {
        "Montserrado": {"unemployment_rate": 0.12, "avg_income": 200},
        "Bong": {"unemployment_rate": 0.18, "avg_income": 150},
        "Nimba": {"unemployment_rate": 0.15, "avg_income": 180}
    }

@router.get("/")
def list_borrowers():
    """Get all borrowers with their risk assessments"""
    return get_all_borrowers()

@router.post("/")
def add_borrower(borrower: BorrowerInput):
    """Add a new borrower and calculate their risk assessment"""
    try:
        # Generate unique ID
        borrower_id = str(uuid.uuid4())[:8]
        
        # Get regional data
        region_data = get_region_stats(borrower.region, REGIONAL_DATA)
        if not region_data:
            region_data = {"unemployment_rate": 0.15, "avg_income": 175}  # Default values
        
        # Create borrower dict for scoring
        borrower_dict = {
            "id": borrower_id,
            "name": borrower.name,
            "region": borrower.region,
            "loan_amount": borrower.loan_amount,
            "base_score": borrower.repayment_rate  # Use repayment rate as base score
        }
        
        # Calculate risk score using intelligence layer
        risk_score = calculate_risk_score(borrower_dict, region_data)
        risk_classification = classify_risk(risk_score)
        
        # Make loan decision using application layer
        policy = get_default_policy()
        is_approved = approve_loan(risk_classification, policy)
        decision = "Approved" if is_approved else "Rejected"
        if risk_classification == "Medium" and is_approved:
            decision = "Conditional"
        
        # Save to database
        conn = connect_db()
        c = conn.cursor()
        c.execute("""
            INSERT INTO borrowers (id, name, region, loan_amount, base_score, adjusted_score, risk, decision)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            borrower_id, borrower.name, borrower.region, borrower.loan_amount,
            borrower.repayment_rate, risk_score, risk_classification, decision
        ))
        conn.commit()
        conn.close()
        
        return {
            "message": f"Borrower {borrower.name} added successfully",
            "id": borrower_id,
            "risk": risk_classification,
            "decision": decision,
            "score": risk_score
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding borrower: {str(e)}")

@router.put("/{borrower_id}")
def update_borrower(borrower_id: str, borrower: BorrowerInput):
    """Update an existing borrower and recalculate risk assessment"""
    try:
        # Get regional data
        region_data = get_region_stats(borrower.region, REGIONAL_DATA)
        if not region_data:
            region_data = {"unemployment_rate": 0.15, "avg_income": 175}
        
        # Create borrower dict for scoring
        borrower_dict = {
            "id": borrower_id,
            "name": borrower.name,
            "region": borrower.region,
            "loan_amount": borrower.loan_amount,
            "base_score": borrower.repayment_rate
        }
        
        # Recalculate risk assessment
        risk_score = calculate_risk_score(borrower_dict, region_data)
        risk_classification = classify_risk(risk_score)
        
        # Make loan decision
        policy = get_default_policy()
        is_approved = approve_loan(risk_classification, policy)
        decision = "Approved" if is_approved else "Rejected"
        if risk_classification == "Medium" and is_approved:
            decision = "Conditional"
        
        # Update database
        conn = connect_db()
        c = conn.cursor()
        c.execute("""
            UPDATE borrowers SET
            name=?, region=?, loan_amount=?, base_score=?, adjusted_score=?, risk=?, decision=?
            WHERE id=?
        """, (
            borrower.name, borrower.region, borrower.loan_amount,
            borrower.repayment_rate, risk_score, risk_classification, decision, borrower_id
        ))
        conn.commit()
        conn.close()
        
        return {
            "message": f"Borrower {borrower_id} updated successfully",
            "risk": risk_classification,
            "decision": decision,
            "score": risk_score
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating borrower: {str(e)}")

@router.delete("/{borrower_id}")
def delete_borrower(borrower_id: str):
    """Delete a borrower"""
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute("DELETE FROM borrowers WHERE id=?", (borrower_id,))
        conn.commit()
        conn.close()
        return {"message": f"Borrower {borrower_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting borrower: {str(e)}")

@router.post("/explain/")
def explain_borrower_risk(borrower: ExplainInput):
    """Generate an AI explanation for a borrower's risk assessment"""
    try:
        # Get regional data
        region_data = get_region_stats(borrower.region, REGIONAL_DATA)
        if not region_data:
            region_data = {"unemployment_rate": 0.15, "avg_income": 175}
        
        # Create borrower dict for analysis
        borrower_dict = {
            "id": borrower.id,
            "name": borrower.name,
            "region": borrower.region,
            "loan_amount": borrower.loan_amount,
            "base_score": borrower.repayment_rate
        }
        
        # Calculate risk score
        risk_score = calculate_risk_score(borrower_dict, region_data)
        risk_classification = classify_risk(risk_score)
        
        # Generate basic explanation
        basic_explanation = generate_explanation(borrower_dict, region_data, risk_score, risk_classification)
        
        # Try to get AI-enhanced explanation
        try:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key:
                prompt = f"""
                Explain why this microloan application received a {risk_classification} risk rating:
                
                Borrower: {borrower.name}
                Region: {borrower.region}
                Loan Amount: ${borrower.loan_amount}
                Repayment History Score: {borrower.repayment_rate}
                Regional Unemployment: {region_data.get('unemployment_rate', 0) * 100:.1f}%
                Regional Average Income: ${region_data.get('avg_income', 0)}
                
                Calculated Risk Score: {risk_score:.3f}
                Risk Classification: {risk_classification}
                
                Provide a clear, concise explanation suitable for loan officers.
                """
                
                ai_explanation = get_llm_response(prompt, groq_api_key)
                return {
                    "choices": [{
                        "message": {
                            "content": ai_explanation
                        }
                    }]
                }
            else:
                return {
                    "choices": [{
                        "message": {
                            "content": basic_explanation
                        }
                    }]
                }
        except Exception as ai_error:
            # Fallback to basic explanation if AI fails
            return {
                "choices": [{
                    "message": {
                        "content": f"{basic_explanation}\n\n(AI explanation unavailable: {str(ai_error)})"
                    }
                }]
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")