
from dotenv import load_dotenv
load_dotenv()

import asyncio
from src.functions.function import patient_check_in, goodbye
from src.client import client
from src.workflows.workflow import GreetingWorkflow

async def main():

    await client.start_service(
        workflows= [GreetingWorkflow],
        functions= [patient_check_in, goodbye]
    )

def run_services():
    asyncio.run(main())

if __name__ == "__main__":
    run_services()