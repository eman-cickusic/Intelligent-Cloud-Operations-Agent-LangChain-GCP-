import datetime
import wikipedia
from langchain_huggingface import HuggingFacePipeline
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools import BaseTool, Tool
from langchain.memory import ConversationBufferMemory
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
def create_base_agent():
   """Creates the base LLM agent with Calculator, Date, and Wikipedia tools."""
   model_name = "google/flan-t5-base"
   tokenizer = AutoTokenizer.from_pretrained(model_name)
   model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to("cpu")
   pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, max_length=512)
   llm = HuggingFacePipeline(pipeline=pipe)
   class CalculatorTool(BaseTool):
       name: str = "Calculator"
       description: str = "Use to evaluate a mathematical expression. Example: '2 + 3 * 5'"
       def _run(self, query: str) -> str:
           try: return str(eval(query, {}, {}))
           except Exception as e: return f"Invalid expression: {e}"
       def _arun(self, query: str): raise NotImplementedError("Async not supported.")
   class DateTool(BaseTool):
       name: str = "DateTool"
       description: str = "Use to get the current date and time."
       def _run(self, query: str = "") -> str: return str(datetime.datetime.now())
       def _arun(self, query: str = ""): raise NotImplementedError("Async not supported.")
   class WikipediaTool(BaseTool):
       name: str = "Wikipedia"
       description: str = "Use to look up a term on Wikipedia and get a summary."
       def _run(self, query: str) -> str:
           try: return wikipedia.summary(query, sentences=2, auto_suggest=False)
           except wikipedia.exceptions.PageError: return f"Could not find a page for '{query}'."
           except wikipedia.exceptions.DisambiguationError as e: return f"Ambiguous query. Options: {e.options[:5]}"
           except Exception as e: return f"Error: {e}"
       def _arun(self, query: str): raise NotImplementedError("Async not supported.")
   tools = [
       Tool(name=t.name, description=t.description, func=t._run, coroutine=t._arun)
       for t in [CalculatorTool(), DateTool(), WikipediaTool()]
   ]
   react_prompt_template = """
   Answer the following questions as best you can. You have access to the following tools:
   {tools}
   Use the following format:
   Question: the input question you must answer
   Thought: you should always think about what to do
   Action: the action to take, should be one of [{tool_names}]
   Action Input: the input to the action
   Observation: the result of the action
   ... (this Thought/Action/Action Input/Observation can repeat N times)
   Thought: I now know the final answer
   Final Answer: the final answer to the original input question
   Begin!
   Question: {input}
   {agent_scratchpad}
   """
   react_prompt = PromptTemplate.from_template(react_prompt_template)
   agent = create_react_agent(llm, tools, react_prompt)
   memory = ConversationBufferMemory(memory_key="chat_history")
   return AgentExecutor(
       agent=agent,
       tools=tools,
       memory=memory,
       verbose=True,
       handle_parsing_errors=True,
       max_iterations=5
   )