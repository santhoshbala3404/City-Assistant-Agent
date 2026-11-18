from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough

prompt1=ChatPromptTemplate.from_messages([
    ('system','you are a code generator'),
    ('human','{topic}')
])

prompt2=ChatPromptTemplate.from_messages([
    ('system','you are a helpful assistant who explains the code inn simple terms'),
    ('human','explain the following in simple words:\n{code}')
])

model = ChatGroq(
    model="llama-3.3-70b-versatile",
)

parser=StrOutputParser()

seq = prompt1 | model | parser 

seq2 = RunnableParallel({
    'code':RunnablePassthrough(),
    'explanation':prompt2 | model | parser
})

chain = seq | seq2
result = chain.invoke({"topic":"write a code on creating linked list in java"})

print(result['code'])
print(result['explanation'])