import gradio as gr
from fastapi import FastAPI
from agents.base_llm_agent import create_base_agent
from agents.gcp_task_agent import create_gcp_task_agent
from agents.devops_query_agent import create_devops_query_agent
# --- Agent Initialization ---
# Create agent executors once to be reused across requests
base_agent_executor = create_base_agent()
gcp_task_agent_executor = create_gcp_task_agent()
devops_query_agent_executor = create_devops_query_agent()
# --- FastAPI App ---
# This will be our main entry point for API calls
app = FastAPI(
   title="All-in-One AI DevOps Agent",
   description="An agent that combines general knowledge, GCP task management, and DevOps querying.",
   version="1.0.0",
)
@app.post("/invoke_agent")
async def invoke_agent(query: str):
   """
   Intelligently routes a query to the appropriate agent.
   - 'task', 'firestore' -> GCP Task Agent
   - 'log', 'bigquery', 'sql' -> DevOps Query Agent
   - Otherwise -> Base LLM Agent
   """
   lower_query = query.lower()
   if any(keyword in lower_query for keyword in ["task", "firestore"]):
       agent_name = "GCP Task Agent"
       executor = gcp_task_agent_executor
   elif any(keyword in lower_query for keyword in ["log", "bigquery", "sql"]):
       agent_name = "DevOps Query Agent"
       executor = devops_query_agent_executor
   else:
       agent_name = "Base LLM Agent"
       executor = base_agent_executor
   try:
       response = executor.invoke({"input": query})
       output = response.get('output', 'Sorry, I could not process the request.')
       return {"agent": agent_name, "response": output}
   except Exception as e:
       return {"agent": agent_name, "error": f"An error occurred: {str(e)}"}
# --- Gradio UI ---
def chat_interface(user_input, history):
   history = history or []
   # Simple routing logic for the UI
   lower_input = user_input.lower()
   if any(keyword in lower_input for keyword in ["task", "firestore"]):
       executor = gcp_task_agent_executor
   elif any(keyword in lower_input for keyword in ["log", "bigquery", "sql", "query"]):
       executor = devops_query_agent_executor
   else:
       executor = base_agent_executor
   try:
       response = executor.invoke({"input": user_input})
       output = response.get('output', 'Sorry, I could not get a response.')
   except Exception as e:
       output = f"⚠️ An unexpected error occurred: {str(e)}"
   history.append((user_input, output))
   return history, ""
with gr.Blocks(theme=gr.themes.Base(), css="#chatbot { height: 600px; }") as demo:
   gr.Markdown("# All-in-One AI DevOps Agent")
   chatbot = gr.Chatbot(elem_id="chatbot")
   with gr.Row():
       txt = gr.Textbox(show_label=False, placeholder="Ask me anything...", container=False, scale=10)
       btn = gr.Button("Send", variant="primary", scale=1)
   gr.Examples(
       examples=[
           "What is the capital of France according to Wikipedia?",
           "What is 15 * (10 + 2)?",
           "Add a new task: Refactor the authentication module",
           "Show me all tasks",
           'Query logs with filter: "severity=ERROR"',
       ],
       inputs=[txt],
       label="Suggestions"
   )
   txt.submit(chat_interface, [txt, chatbot], [chatbot, txt])
   btn.click(chat_interface, [txt, chatbot], [chatbot, txt])
# Mount the Gradio app on top of the FastAPI app
app = gr.mount_gradio_app(app, demo, path="/")
if __name__ == "__main__":
   import uvicorn
   uvicorn.run(app, host="0.0.0.0", port=7860)