from datetime import timedelta
from restack_ai.workflow import workflow
from src.functions.function import patient_check_in, goodbye, InputParams


@workflow.defn(name="GreetingWorkflow",sandboxed=False)
class GreetingWorkflow:
    @workflow.run
    async def run(self, input : InputParams):
        for i in range(10):
            input.days_since_start = i
            await workflow.step(patient_check_in, input, start_to_close_timeout=timedelta(seconds=600))
    async def goodbye(self):
        return await workflow.step(goodbye, InputParams("world"), start_to_close_timeout=timedelta(seconds=10))


