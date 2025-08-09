from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline
from utils.gcp_helpers import add_task_to_firestore, get_tasks_from_firestore, trigger_cloud_function
def create_gcp_task_agent():
   """Creates an agent for managing tasks in Firestore and triggering cloud functions."""
   pipe = pipeline("text2text-generation", model="google/flan-t5-base", max_length=512)
   llm = HuggingFacePipeline(pipeline=pipe)
   tools = [
       Tool(
           name="AddTaskToFirestore",
           func=add_task_to_firestore,
           description="Use to create a new task in Firestore. Input should be the task description."
       ),
       Tool(
           name="GetTasksFromFirestore",
           func=lambda _: get_tasks_from_firestore(),
           description="Use to retrieve all current tasks from Firestore."
       ),
       Tool(
           name="TriggerCloudFunction",
           func=trigger_cloud_function,
           description='Use to trigger an HTTP Cloud Function. Input must be a string containing the function URL followed by a JSON payload, like \'https://your-url {"key": "value"}\'.'
       )
   ]
   react_prompt = PromptTemplate.from_template(
       """You are a helpful GCP assistant. Your job is to manage tasks and trigger actions.
       Use the available tools to answer the user's request.
       Tools:
       {tools}
       Request: {input}
       {agent_scratchpad}
       """
   )
   agent = create_react_agent(llm, tools, react_prompt)
   return AgentExecutor(agent=agent, tools=tools, verbose=True)