"""
Test script to verify auto-activation of WatsonX Orchestrate environment
"""
import os
import time
from dotenv import load_dotenv
from watsonx_client import WatsonXClient


def test_auto_activation():
    """Test that WatsonXClient automatically activates environment on creation"""
    print("🔧 Testing Auto-Activation of WatsonX Orchestrate Environment")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ['WXO_BASE_URL', 'WXO_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return
    
    print("✅ Environment variables loaded")
    print(f"Environment: {os.getenv('WXO_ENVIRONMENT', 'build_engg')}")
    print(f"Base URL: {os.getenv('WXO_BASE_URL')}")
    
    print("\n🔄 Creating WatsonXClient (should auto-activate environment)...")
    
    # Create client - this should automatically activate the environment
    start_time = time.time()
    client = WatsonXClient(force_refresh_on_every_request=False)
    end_time = time.time()
    
    print(f"✅ WatsonXClient created in {end_time - start_time:.2f} seconds")
    
    # Test that the client works by listing agents
    print("\n🔄 Testing client functionality by listing agents...")
    
    try:
        agents = client.list_native_agents()
        print(f"✅ Successfully listed {len(agents)} native agents")
        
        if agents:
            print(f"First agent: {agents[0].get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error listing agents: {e}")
        return
    
    print("\n🔄 Testing agent invocation...")
    
    try:
        # Get first agent for testing
        if agents:
            first_agent = agents[0]
            agent_id = first_agent.get('id')
            agent_name = first_agent.get('name')
            
            print(f"Testing with agent: {agent_name}")
            
            result = client.invoke_agent(
                agent_id=agent_id,
                message="Hello! This is a test message from auto-activated client."
            )
            
            if result["status"] == "success":
                print("✅ Agent invocation successful!")
                print(f"Thread ID: {result.get('thread_id')}")
            else:
                print(f"❌ Agent invocation failed: {result['error']}")
        else:
            print("No agents available for testing")
            
    except Exception as e:
        print(f"❌ Error invoking agent: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Auto-activation test completed!")


def test_multiple_clients():
    """Test creating multiple clients to ensure each one auto-activates"""
    print("\n🔧 Testing Multiple Client Creation")
    print("=" * 40)
    
    print("Creating first client...")
    client1 = WatsonXClient(force_refresh_on_every_request=False)
    
    print("Creating second client...")
    client2 = WatsonXClient(force_refresh_on_every_request=True)
    
    print("Creating third client...")
    client3 = WatsonXClient(force_refresh_on_every_request=False)
    
    print("✅ All clients created successfully")
    
    # Test that all clients work
    print("\nTesting all clients...")
    
    try:
        agents1 = client1.list_native_agents()
        print(f"Client 1: {len(agents1)} agents")
        
        agents2 = client2.list_native_agents()
        print(f"Client 2: {len(agents2)} agents")
        
        agents3 = client3.list_native_agents()
        print(f"Client 3: {len(agents3)} agents")
        
        print("✅ All clients working correctly")
        
    except Exception as e:
        print(f"❌ Error testing clients: {e}")


def main():
    """Main test function"""
    print("🚀 Testing WatsonX Orchestrate Auto-Activation")
    print("=" * 60)
    
    # Test auto-activation
    test_auto_activation()
    
    # Test multiple clients
    test_multiple_clients()
    
    print("\n" + "=" * 60)
    print("✅ All auto-activation tests completed!")


if __name__ == "__main__":
    main() 