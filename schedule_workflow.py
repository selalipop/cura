import phonenumbers
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

import asyncio
import time
import pypdf
import io
from restack_ai import Restack

from src.functions.function import InputParams


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
    st.title("Patient Workflow System")

    # Create input fields
    patient_name = st.text_input("Patient Name")
    patient_phone = st.text_input("Patient Phone Number")

    # File uploader for PDF
    uploaded_file = st.file_uploader("Upload Patient Plan (PDF)", type="pdf")

    if st.button("Submit") and uploaded_file is not None:
        with st.spinner("Processing..."):
            # Read the PDF content
            plan_text = read_pdf(uploaded_file)
            parsed_patient_phone = phonenumbers.parse(patient_phone, "US")
            formatted_patient_phone = phonenumbers.format_number(parsed_patient_phone, phonenumbers.PhoneNumberFormat.E164)

            # Run the workflow
            result = asyncio.run(
                process_workflow(
                    name=patient_name, plan_text=plan_text, phone=formatted_patient_phone
                )
            )

            # Display the result
            st.success("Workflow completed!")
            st.json(result)


if __name__ == "__main__":
    main()
