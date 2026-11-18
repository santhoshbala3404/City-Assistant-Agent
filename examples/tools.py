from dotenv import load_dotenv
load_dotenv()

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

search_prompt=TavilySearchResults(max_results=6)

model = ChatGroq(model="llama-3.3-70b-versatile")

prompt=ChatPromptTemplate.from_template(    """
you are a helpful assistant who summarises the following news into clear bullet points.max
{news}
"""
)

chain=prompt | model | StrOutputParser()
news_result=search_prompt.run("Latest news from Tamil Nadu")
result=chain.invoke({'news':news_result})
print(result)

