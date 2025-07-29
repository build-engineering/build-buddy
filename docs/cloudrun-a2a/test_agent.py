#!/usr/bin/env python3
"""
Simple test script for the WatsonOrchestrateAgent
"""
import asyncio
from watson_orchestrate_agent import WatsonOrchestrateAgent


async def test_agent():
    """Test the WatsonOrchestrateAgent with a simple query"""
    print("🤖 Testing WatsonOrchestrateAgent")
    print("=" * 50)
    
    try:
        # Create the agent
        agent = WatsonOrchestrateAgent()
        print("✅ Agent created successfully")
        
        # Test with a simple query
        query = "List all native agents in WatsonX Orchestrate"
        query = "Can you invoke this agent with id 6bd47759-6db8-4645-ac3e-68de42e3821c, with this message: 'Hello!!' and give me the output"
        print(f"\n🔄 Testing query: '{query}'")
        
        result = await agent.ainvoke(query)
        print(f"✅ Response:\n{result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have:")
        print("   - WXO_API_KEY set in your .env file")
        print("   - WXO_BASE_URL set in your .env file")
        print("   - OPENAI_API_KEY set in your .env file")


if __name__ == "__main__":
    asyncio.run(test_agent()) 