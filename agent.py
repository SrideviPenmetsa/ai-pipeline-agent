from dotenv import load_dotenv
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

load_dotenv()

# --- 1. Set up the Vector Database for Incidents ---
# Initialize the embedding model
embeddings = OpenAIEmbeddings()

# Convert your historical incidents into LangChain Document objects
past_incidents_data = [
    Document(
        page_content="2024-03-15: FileNotFoundError on sales_etl DAG. Fixed by adding S3 existence check in upstream task. Resolution time: 45 mins.",
        metadata={"error_type": "FileNotFoundError"}
    ),
    Document(
        page_content="2024-04-02: OperationalError. Redshift connection pool exhausted during peak load. Fixed by increasing max_connections. Resolution: 2 hours.",
        metadata={"error_type": "OperationalError"}
    ),
    Document(
        page_content="2024-02-28: MemoryError in customer_data DAG OOM. Fixed by adding repartition(200) before join. Resolution: 1 hour.",
        metadata={"error_type": "MemoryError"}
    )
]

# Create an in-memory Chroma vector store populated with the documents
incident_vdb = Chroma.from_documents(
    documents=past_incidents_data, 
    embedding=embeddings,
    collection_name="past_pipeline_incidents"
)

# --- 2. Define tools the agent can use ---
@tool
def analyze_airflow_log(log_text: str) -> str:
    """Analyzes an Airflow task log and identifies the error type."""
    if "FileNotFoundError" in log_text:
        return "Root cause: Missing S3 file. The upstream task likely failed to write the file."
    elif "OperationalError" in log_text:
        return "Root cause: Database connection issue. Check Redshift cluster status."
    elif "MemoryError" in log_text:
        return "Root cause: Out of memory. PySpark job needs more executor memory."
    else:
        return f"Unknown error pattern. Raw log: {log_text[:200]}"

@tool  
def get_similar_past_incidents(query: str) -> str:
    """Searches the incident vector database for past pipeline failures similar to the given query."""
    # Perform a similarity search against the vector database
    # k=1 returns the single most relevant past incident
    results = incident_vdb.similarity_search(query, k=1)
    
    if results:
        # Return the text of the matched document
        return results[0].page_content
    return "No similar past incidents found."

# --- 3. Set up the agent ---
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

tools = [analyze_airflow_log, get_similar_past_incidents]

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert data engineering incident analyst. 
    When given a pipeline failure log, you:
    1. Analyze the log to identify the root cause
    2. Search for similar past incidents  
    3. Provide a clear diagnosis and recommended fix
    Be concise and actionable."""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- Test it with a fake Airflow log ---
fake_log = """
[2025-05-26 09:15:23] Task failed: customer_etl.load_to_redshift
[2025-05-26 09:15:23] Traceback (most recent call last):
[2025-05-26 09:15:23] FileNotFoundError: s3://data-lake/customers/2025-05-26/raw.parquet not found
[2025-05-26 09:15:23] Task instance marked as FAILED
"""

result = agent_executor.invoke({
    "input": f"This Airflow DAG just failed. Please diagnose and recommend a fix:\n{fake_log}"
})

print("\n=== AGENT DIAGNOSIS ===")
print(result["output"])