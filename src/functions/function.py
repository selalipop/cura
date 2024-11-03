import os
from restack_ai.function import function
from dataclasses import dataclass
import asyncio
from vapi import AssistantOverrides, AsyncVapi, CreateCustomerDto
import weave
weave.init("cura-weave")


@dataclass
class InputParams:
    patient_name: str
    patient_phone: str
    patient_plan: str
    days_since_start: int


@function.defn(name="goodbye")
async def goodbye(input: InputParams) -> str:
    return f"Goodbye, {input.name}!"





@function.defn(name="patient_check_in")
@weave.op()
async def patient_check_in(input: InputParams) -> str:
    print(input)
    print(os.getenv("VAPI_API_KEY"))
    vapi = AsyncVapi(
        token=os.getenv("VAPI_API_KEY"),
    )
    call = await vapi.calls.create(
        phone_number_id=os.getenv("VAPI_PHONE_NUMBER_ID"),
        assistant_id=os.getenv("VAPI_ASSISTANT_ID"),
        customer=CreateCustomerDto(
            name=input.patient_name,
            number=input.patient_phone,
        ),
        assistant_overrides=AssistantOverrides(
            variable_values={
                "patient_name": input.patient_name,
                "patient_phone": input.patient_phone,
                "patient_plan": input.patient_plan,
                "days_since_start": input.days_since_start or 1,
            }
        ),
    )
    while True:
        call_status = await vapi.calls.get(call.id)
        if call_status.status == "ended":
            break
        await asyncio.sleep(1)
    return {"status": "success"}