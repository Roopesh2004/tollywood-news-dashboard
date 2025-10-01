import os
from dotenv import load_dotenv
import google.generativeai as genai
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from crewai.llm import LLM
from newsapi import NewsApiClient
from newspaper import Article
from datetime import datetime, timedelta, timezone
import streamlit as st

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not NEWSAPI_KEY or not GOOGLE_API_KEY:
    st.error("NEWSAPI_KEY or GOOGLE_API_KEY not found in .env")
    st.stop()

# ------------------------------
# Streamlit UI
# ------------------------------
st.set_page_config(page_title="Tollywood News Dashboard", layout="wide")
st.title("🎬 Tollywood News Dashboard")
st.markdown("""
Fetch the latest Tollywood news, read the top headlines, and get a **detailed AI-generated summary**.
Powered by **NewsAPI**, **Google Gemini**, and **CrewAI**.
""")

# Button to fetch news
if st.button("🔍 Fetch & Summarize News"):

    with st.spinner("Fetching Tollywood news..."):
        # Fetch news
        newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
        from_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')
        articles = newsapi.get_everything(
            q='"Tollywood" OR "Telugu cinema" OR "Telugu movies"',
            from_param=from_date,
            language="en",
            sort_by="relevancy",
            page_size=5
        )

        # Display top headlines
        if articles['totalResults'] > 0:
            st.subheader("Top 5 Tollywood News Headlines")
            for i, article in enumerate(articles['articles'], 1):
                st.markdown(f"**{i}. {article['title']}**")
                st.markdown(f"Source: {article['source']['name']} | [Read more]({article['url']})")
                st.markdown("---")
        else:
            st.warning("No Tollywood news found in the last 7 days.")

        # Scrape full articles for summary
        full_text = ""
        for article in articles.get('articles', []):
            try:
                news_article = Article(article['url'])
                news_article.download()
                news_article.parse()
                full_text += news_article.text + "\n\n"
            except Exception as e:
                print(f"Skipping article: {article['title']} - {e}")

        if not full_text.strip():
            full_text = "No full text available for Tollywood news."

    st.success("✅ News fetched successfully!")

    # ------------------------------
    # Define Gemini Tool
    # ------------------------------
    class GeminiTool(BaseTool):
        name: str = "ask_gemini"
        description: str = "Ask Google Gemini for a response to the given prompt"
        def _run(self, prompt: str) -> str:
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"An error occurred while calling Gemini: {e}"

    # ------------------------------
    # Run CrewAI to generate summary
    # ------------------------------
    genai.configure(api_key=GOOGLE_API_KEY)
    llm = LLM(model="gemini/gemini-2.5-flash", temperature=0.2, max_output_tokens=500, api_key=GOOGLE_API_KEY)
    ask_gemini_tool = GeminiTool()

    thinker = Agent(
        role="Thinker",
        goal="Summarize Tollywood news using the Gemini API.",
        backstory="You are an AI researcher generating detailed summaries from news articles.",
        tools=[ask_gemini_tool],
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    responder = Agent(
        role="Responder",
        goal="Polish the summary in a readable and user-friendly way.",
        backstory="You are a helpful assistant that makes content clear and concise.",
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    task1 = Task(
        agent=thinker,
        description=f"""
Summarize the following Tollywood news in a detailed, informative paragraph.
Include key highlights, movie names, events, actors, and important updates.
Write it in a smooth, readable style, around 4-6 sentences:

{full_text}
""",
        expected_output="A detailed Tollywood news summary."
    )

    task2 = Task(
        agent=responder,
        description="Take the raw summary from the Thinker and rewrite it to be clear, concise, and user-friendly.",
        expected_output="A polished summary."
    )

    crew = Crew(agents=[thinker, responder], tasks=[task1, task2], verbose=False)

    with st.spinner("Generating AI summary..."):
        result = crew.kickoff()

    st.success("✅ Summary Generated!")
    st.subheader("📝 AI-Generated Tollywood News Summary")
    st.text_area("Summary", value=result, height=300)
