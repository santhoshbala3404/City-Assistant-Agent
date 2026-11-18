# City Assistant Agent

A command-line AI agent built with LangChain and Groq that answers questions about cities. It decides on its own when to call tools, fetches live weather and breaking news for one or many cities, and then writes a polished, news-presenter-style summary.

## Features

- Tool-calling agent loop: the LLM chooses which tools to call, reads the results, and keeps going until it has a final answer.
- Live weather via the OpenWeatherMap API (temperature, feels-like, humidity, wind speed, conditions).
- Latest news via the Tavily Search API, limited to recent articles.
- Multi-city support: pass "Delhi, Mumbai, Bangalore" and every city is handled in a single tool call.
- Conversation memory within a session, so follow-up questions work.
- Prompt-engineered output: descriptive paragraphs with headings, no raw tool dumps.

## How It Works

```
User question
      |
      v
LLM (Groq, gpt-oss-120b) with tools bound
      |
      |-- needs data? --> calls get_weather / get_news
      |                         |
      |<------ tool results ----|
      v
Final summarised answer printed to the terminal
```

1. The user's message is added to the conversation history.
2. The model is invoked with the tools `get_weather` and `get_news` bound to it.
3. If the response contains `tool_calls`, each tool is executed and its result is appended as a `ToolMessage`.
4. The model is invoked again with the tool results. This repeats until no more tool calls are requested.
5. The final text response is printed.

## Project Structure

```
city-assistant-agent/
├── cityagent.py            # Main project: weather + news agent
├── examples/               # Smaller LangChain learning experiments
│   ├── customtools.py            # Minimal custom tool (text length) with tool calling
│   ├── tools.py                  # Tavily search + LLM bullet-point summary chain
│   ├── runnables.py              # RunnableParallel with RunnableLambda
│   └── runnablepassthrough.py    # RunnablePassthrough: generate code, then explain it
├── requirements.txt
├── .env.example            # Template for API keys
├── .gitignore
└── README.md
```

## Tech Stack

- Python 3.10+
- LangChain (core, community, Groq integration)
- Groq (LLM inference)
- OpenWeatherMap API
- Tavily Search API
- python-dotenv, requests, rich

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/city-assistant-agent.git
cd city-assistant-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Copy the example file and add your own keys:

```bash
cp .env.example .env
```

| Variable | Used for | Where to get it |
|---|---|---|
| `GROQ_API_KEY` | LLM inference | https://console.groq.com/keys |
| `OPENWEATHER_API_KEY` | Weather data | https://home.openweathermap.org/api_keys |
| `TAVILY_API_KEY` | News search | https://app.tavily.com/ |

All three services offer a free tier.

### 5. Run the agent

```bash
python cityagent.py
```

Type `0` to quit.

## Example Usage

```
You : What's the weather and latest news in Bangalore and Hyderabad?
```

The agent calls `get_weather("Bangalore, Hyderabad")` and `get_news("Bangalore, Hyderabad")`, then responds with a heading per city, a weather summary, and descriptive paragraphs explaining each news story and why it matters.

Other things to try:

- "Weather in Delhi, Mumbai and Chennai"
- "Any breaking news in Mysuru today?"
- "Compare the weather in Pune and Kolkata" (then a follow-up like "Which one is better for a trip?")

## Tools

### get_weather(cities: str)
Accepts a comma-separated string of cities, calls the OpenWeatherMap current weather endpoint for each, and returns formatted conditions. Cities that cannot be found return a friendly "Unable to fetch weather" line instead of crashing.

### get_news(cities: str)
Accepts a comma-separated string of cities, searches Tavily (advanced depth, top 3 results per city) for recent news, and returns titles and content for the LLM to summarise.

## The Examples Folder

These scripts are small, focused experiments that build up to the main agent:

| File | Concept demonstrated |
|---|---|
| `customtools.py` | Defining a tool with `@tool`, binding it to an LLM, executing the tool call manually |
| `tools.py` | Using a search tool and piping results into a prompt, model, and parser chain (LCEL) |
| `runnables.py` | Running independent chains concurrently with `RunnableParallel` and `RunnableLambda` |
| `runnablepassthrough.py` | Passing a previous step's output through unchanged alongside a new computation |

## Configuration

You can tweak the model in `cityagent.py`:

```python
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    max_tokens=1024,
)
```

Any Groq model that supports tool calling will work (for example `llama-3.3-70b-versatile`).

## Known Limitations

- No retry or timeout handling on external API calls.
- The weather tool depends on OpenWeatherMap recognising the city name as typed.
- News quality depends on what Tavily returns for the query.
- Conversation history is kept in memory only and resets when the program exits.

## Future Improvements

- Add a web UI with Streamlit or Gradio.
- Add timeouts, retries, and better error handling.
- Add a 5-day forecast tool.
- Persist chat history.
- Migrate to LangGraph for more advanced agent workflows.

