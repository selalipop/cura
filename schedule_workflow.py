import phonenumbers 
import streamlit as st
from dotenv import load_dotenv
import asyncio
import time
import pypdf
import io
from restack_ai import Restack
from src.functions.function import InputParams
from patient_alert import PatientAlert
import json
import pandas as pd
from filelock import FileLock
import threading

def read_alerts(filename="alerts.json"):
    try:
        with FileLock(filename + ".lock"):
            with open(filename, "r") as f:
                data = json.load(f)
                return [PatientAlert(**alert) for alert in data]
    except FileNotFoundError:
        return []

def poll_alerts():
    while True:
        alerts = read_alerts()
        if alerts:
            # Convert alerts to DataFrame for nice display
            df = pd.DataFrame(
                [(a.priority, a.reason, a.excerpt) for a in alerts],
                columns=["Priority", "Reason", "Excerpt"]
            )
            # Sort by priority (highest first)
            df = df.sort_values("Priority", ascending=False)
            
            # Update Streamlit display
            with alert_table:
                st.table(df)
        time.sleep(5)  # Poll every 5 seconds

async def process_workflow(name, plan_text, phone):
    client = Restack()
    
    workflow_id = f"{int(time.time() * 1000)}-GreetingWorkflow"
    runId = await client.schedule_workflow(
        workflow_name="GreetingWorkflow",
        workflow_id=workflow_id,
        input=InputParams(
            patient_name=name,
            patient_phone=phone,
            patient_plan=plan_text,
            days_since_start=0,
        ),
    )
    
    result = await client.get_workflow_result(workflow_id=workflow_id, run_id=runId)
    return result

def read_pdf(pdf_file):
    pdf_reader = pypdf.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def main():
    st.title("Cura Provider Portal: Patient 3405-2AB")
    
    
    # Read and display alerts
    alerts = read_alerts()
    if alerts:
        df = pd.DataFrame(
            [(a.priority, a.reason, a.excerpt) for a in alerts],
            columns=["Priority", "Reason", "Excerpt"]
        )
        df = df.sort_values("Priority", ascending=False)
        st.table(df)

    # Create input fields
    patient_name = st.text_input("Patient Name")
    patient_phone = st.text_input("Patient Phone Number")
    
    # File uploader for PDF
    uploaded_file = st.file_uploader("Upload Patient Plan (PDF)", type="pdf")
    
    if st.button("Submit") and uploaded_file is not None:
        with st.spinner("Processing..."):
            plan_text = read_pdf(uploaded_file)
            parsed_patient_phone = phonenumbers.parse(patient_phone, "US")
            formatted_patient_phone = phonenumbers.format_number(
                parsed_patient_phone, 
                phonenumbers.PhoneNumberFormat.E164
            )
            
            result = asyncio.run(
                process_workflow(
                    name=patient_name, 
                    plan_text=plan_text, 
                    phone=formatted_patient_phone
                )
            )
            
            st.success("Workflow completed!")
            st.json(result)

if __name__ == "__main__":
    main()