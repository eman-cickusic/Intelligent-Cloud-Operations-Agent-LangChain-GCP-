from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline
from utils.gcp_helpers import (
   query_gcp_logs,
   execute_bigquery_query,
   query_gcp_metrics,
   query_terraform_state
)
def create_devops_query_agent():
   """Creates an agent for querying all GCP DevOps data."""
   pipe = pipeline("text2text-generation", model="google/flan-t5-base", max_length=1024)
   llm = HuggingFacePipeline(pipeline=pipe)
   tools = [
       Tool(
           name="QueryGCPLogs",
           func=query_gcp_logs,
           description="Use to query Google Cloud logs. Input must be a valid GCP logging filter string."
       ),
       Tool(
           name="QueryBigQuery",
           func=execute_bigquery_query,
           description="Use to execute a SQL query on BigQuery. Input must be a valid SQL query."
       ),
       Tool(
           name="QueryGCPMetrics",
           func=query_gcp_metrics,
           description='Use to query Google Cloud Monitoring metrics. Input must be a valid metric filter, like \'metric.type = "compute.googleapis.com/instance/cpu/utilization"\'.'
       ),
       Tool(
           name="QueryTerraformState",
           func=query_terraform_state,
           description="Use to list resources from a Terraform state file in a GCS bucket. Input must be in the format 'bucket-name/resource_type', for example 'my-tf-bucket/google_compute_instance'."
       )
   ]
   react_prompt = PromptTemplate.from_template(
       """You are a DevOps assistant. Your purpose is to query GCP data, metrics, logs, and infrastructure state.
       Use the available tools to answer the user's request.
       Tools:
       {tools}
       Request: {input}
       {agent_scratchpad}
       """
   )
   agent = create_react_agent(llm, tools, react_prompt)
   return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)