"""
Simple OpenAI test to isolate the proxies issue
"""

import os
import openai
import config

def test_openai_simple():
    """Simple OpenAI test"""
    print("🧪 Testing OpenAI client creation...")
    
    # Clear any proxy environment variables that might interfere
    env_vars_to_clear = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']
    original_values = {}
    
    for var in env_vars_to_clear:
        if var in os.environ:
            original_values[var] = os.environ[var]
            del os.environ[var]
    
    try:
        print(f"OpenAI version: {openai.__version__}")
        print("Creating OpenAI client...")
        
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        print("✅ OpenAI client created successfully!")
        
        # Test a simple API call
        print("Testing API call...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'Hello' in Russian"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ API call successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False
    
    finally:
        # Restore original environment variables
        for var, value in original_values.items():
            os.environ[var] = value

if __name__ == "__main__":
    test_openai_simple() 