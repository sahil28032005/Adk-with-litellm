import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from agent import root_agent  # Import your existing agent

# Initialize Vertex AI
PROJECT_ID = "core-incentive-437723-m8"  # Your project ID from .env
LOCATION = "us-central1"  # The location you set in .env
STAGING_BUCKET = "gs://staging-dev-9878"  # Replace with your GCS bucket

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
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
        ]
    )
    
    print(f"Deployment complete. Resource name: {remote_app.resource_name}")
    return remote_app

# Get existing deployed agent
def get_existing_agent():
    # Your agent resource name from the previous deployment
    agent_name = 'projects/1039845468888/locations/us-central1/reasoningEngines/6616007754932813824'
    print(f"Getting existing agent: {agent_name}")
    return agent_engines.get(agent_name)

# Test the deployed agent
def test_remote_agent(remote_app):
    print("Testing deployed agent...")
    remote_session = remote_app.create_session(user_id="remote_test_user")
    print(f"Created remote session: {remote_session}")
    
    for event in remote_app.stream_query(
        user_id="remote_test_user",
        session_id=remote_session["id"],
        message="What's the current time in New York?",
    ):
        print(event)
    
    print("Remote test completed.")

if __name__ == "__main__":
    # Uncomment the functions you want to run
    test_locally()
    # remote_app = deploy_to_agent_engine()  # Comment this out to avoid redeployment
    
    # Use this to test the existing deployed agent
    # remote_app = get_existing_agent()
    # test_remote_agent(remote_app)