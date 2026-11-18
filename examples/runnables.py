from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableParallel, RunnableLambda

prompt1=ChatPromptTemplate.from_template(
    'explain advantages of {topic}'
)

prompt2=ChatPromptTemplate.from_template(
    'explain disadvantages of {topic}'
)

model = ChatGroq(
    model="llama-3.3-70b-versatile",
)

parser=StrOutputParser()

chain = RunnableParallel({
    'short': RunnableLambda(lambda x : x['short']) | prompt1 | model | parser,
    "detail": RunnableLambda(lambda x : x['detail']) | prompt2 | model | parser
})

result=chain.invoke({
    'short':{'topic':'Extreme value theory'},
    'detail':{'topic':'Peak over threshold'}

})

print(result['short'])
print(result['detail'])