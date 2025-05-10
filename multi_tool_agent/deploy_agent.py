import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from agent import root_agent  # Import your existing agent

import time
import random

# Initialize Vertex AI
PROJECT_ID = ""  # Your project ID from .env
LOCATION = "us-central1"  # The location you set in .env
STAGING_BUCKET = ""  # Replace with your GCS bucket

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# Prepare your agent for Agent Engine
app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

# Test locally before deployment


def test_locally():
    print("Testing agent locally...")
    session = app.create_session(user_id="test_user")
    print(f"Created session: {session.id}")

    for event in app.stream_query(
        user_id="test_user",
        session_id=session.id,
        message="What's the weather in New York?",
    ):
        print(event)

    print("Local test completed.")

# Deploy to Agent Engine


def deploy_to_agent_engine():
    print("Deploying agent to Vertex AI Agent Engine...")
    remote_app = agent_engines.create(
        agent_engine=root_agent,
        display_name="Weather Time Agent",  # Add a display name
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
            "cloudpickle==3.1.1",
            "pydantic==2.11.4",
            "tzdata",  # Add this for ZoneInfo
        ],
        extra_packages=["./extra_packages"]
    )
    
    print(f"Deployment complete. Resource name: {remote_app.resource_name}")
    return remote_app

# Get existing deployed agent
# Get existing deployed agent
def get_existing_agent():
    # Your agent resource name from the most recent deployment
    # Use the one from your list_deployments() output
    agent_name = 'projects/1039845468888/locations/us-central1/reasoningEngines/9136475433888382976'
    print(f"Getting existing agent: {agent_name}")
    return agent_engines.get(agent_name)

# Test the deployed agent
# Test the deployed agent with retry logic
def test_remote_agent(remote_app, max_retries=5):
    print("Testing deployed agent...")
    
    for attempt in range(max_retries):
        try:
            remote_session = remote_app.create_session(user_id="remote_test_user")
            print(f"Created remote session: {remote_session}")
            
            for event in remote_app.stream_query(
                user_id="remote_test_user",
                session_id=remote_session["id"],
                message="What's the current time in New York?",
            ):
                print(event)
            
            print("Remote test completed successfully.")
            return
        except Exception as e:
            print(f"Attempt {attempt+1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                print("All retry attempts failed. Please check the logs for more details.")

# List all deployed agents
def list_deployments():
    """Lists all deployed agents in the current project and location."""
    print(f"Listing all deployed agents in project {PROJECT_ID}, location {LOCATION}...")
    
    # Get all reasoning engines (agents) in the project
    agents = list(agent_engines.list())  # Convert generator to list
    
    if not agents:
        print("No deployed agents found.")
        return []

    print(f"Found {len(agents)} deployed agent(s):")
    for i, agent in enumerate(agents, 1):
        print(f"{i}. Name: {agent.display_name}")
        print(f"   Resource name: {agent.resource_name}")
        print(f"   Create time: {agent.create_time}")
        print(f"   Update time: {agent.update_time}")
        print("   -----------------------------")
    
    return agents

if __name__ == "__main__":
    # Uncomment the functions you want to run
    # test_locally()
    remote_app = deploy_to_agent_engine()  # Comment this out to avoid redeployment
    
    # Use this to test the existing deployed agent
    # remote_app = get_existing_agent()
    test_remote_agent(remote_app)
    
    # List all deployed agents
    # list_deployments()