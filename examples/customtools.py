from dotenv import load_dotenv
load_dotenv()

from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from rich import print

@tool
def get_text_length(text:str)->int:
    """Return the number of characters in a given text."""
    return len(text)

tools={
    'get_text_length':get_text_length
}
llm=ChatGroq(model="llama-3.3-70b-versatile")

llm_with_tool=llm.bind_tools([get_text_length])
message=[]
prompt=input("You: ")
query=HumanMessage(prompt)
message.append(query)

result=llm_with_tool.invoke(message)
message.append(result)

if result.tool_calls:
    tool_name=result.tool_calls[0]['name']
    tool_message=tools[tool_name].invoke(result.tool_calls[0])
    message.append(tool_message)

result=llm_with_tool.invoke(message)
print(result)



