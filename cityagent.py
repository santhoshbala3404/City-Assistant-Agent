from dotenv import load_dotenv
load_dotenv()

import os
import requests

from tavily import TavilyClient

from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

##########################################################
# WEATHER TOOL
##########################################################

@tool
def get_weather(cities: str) -> str:
    """
    Get the current weather for one or more cities.
    Example input: "Bangalore, Hyderabad"
    """

    api_key = os.getenv("OPENWEATHER_API_KEY")

    outputs = []

    for city in [c.strip() for c in cities.split(",")]:

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={api_key}&units=metric"
        )

        response = requests.get(url)
        data = response.json()

        if str(data.get("cod")) != "200":
            outputs.append(f"{city}: Unable to fetch weather.")
            continue

        outputs.append(
            f"""
        City: {city}
        Condition: {data['weather'][0]['description'].title()}
        Temperature: {data['main']['temp']}°C
        Feels Like: {data['main']['feels_like']}°C
        Humidity: {data['main']['humidity']}%
        Wind Speed: {data['wind']['speed']} m/s
        """
        )

    return "\n".join(outputs)

##########################################################
# NEWS TOOL
##########################################################

@tool
def get_news(cities: str) -> str:
    """
    Get latest news for one or more cities.
    Example input: "Delhi, Mumbai"
    """

    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    final_news = []

    for city in [c.strip() for c in cities.split(",")]:

        response = tavily.search(
            query=f"""Breaking news today in {city}.
            Only include news from today or the last 5 days.
            Ignore old articles.""",
            max_results=3,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
        )

        results = response.get("results", [])

        if not results:
            final_news.append(f"No news found for {city}.")
            continue

        city_news = [f"\n### {city}\n"]

        for article in results:

            title = article.get("title", "")

            content = (
                article.get("content")
                or article.get("raw_content")
                or ""
            )

            city_news.append(
                f"""
            Title:
           {title}

            Details:
           {content}
            """)

        final_news.append("\n".join(city_news))

    return "\n\n".join(final_news)


##########################################################
# LLM
##########################################################

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    max_tokens=1024
)

tools = {
    "get_weather": get_weather,
    "get_news": get_news,
}

LLM_with_tools = llm.bind_tools([get_weather, get_news])


##########################################################
# SYSTEM PROMPT
##########################################################

messages = [
    SystemMessage(
        content="""
You are an intelligent City Assistant.

Rules:

1. Use tools whenever required.

2. If the user asks for weather and news together,
call BOTH tools before answering.

3. Never copy raw tool output.

4. For news:
- Summarize every news item.
- Explain what happened.
- Explain why it is important.
- Combine similar news.
- Write in descriptive paragraph form.
- Do NOT simply list URLs.
- Mention the source URL only at the end if useful.

5. Format responses nicely using headings.

6. Sound like a professional news presenter.

If the user asks about multiple cities:

- Use ONE tool call.
- Pass all requested cities separated by commas.
- Example:
  get_weather(cities="Bangalore, Hyderabad")
  get_news(cities="Delhi, Mumbai")

Never ignore any city. 
Also give it descriptively and don't use any kind of bold or italics formatting.
"""
    )
]


##########################################################
# CHAT LOOP
##########################################################

while True:
    
  
    print("\nCity Agent is ready! Enter 0 to quit.")

    prompt = input("You : ")

    if prompt == "0":
        break

    messages.append(HumanMessage(content=prompt))

    response = LLM_with_tools.invoke(messages)

    messages.append(response)

    while response.tool_calls:

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]

            tool_response = tools[tool_name].invoke(tool_call)

            messages.append(tool_response)

        response = LLM_with_tools.invoke(messages)

        messages.append(response)

    print("\nBot:\n")
    print(response.content)