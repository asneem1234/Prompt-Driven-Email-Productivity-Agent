"""
Simple test script to verify all components work
Run with: python test_components.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from src.llm_client import LLMClient
        from src.prompt_manager import PromptManager
        from src.email_processor import EmailProcessor
        from src.draft_manager import DraftManager
        from src.email_agent import EmailAgent
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_prompt_manager():
    """Test prompt manager"""
    print("\nTesting Prompt Manager...")
    try:
        from src.prompt_manager import PromptManager
        
        pm = PromptManager()
        prompts = pm.get_all_prompts()
        
        assert len(prompts) > 0, "No prompts loaded"
        assert "categorization" in prompts, "Missing categorization prompt"
        
        # Test formatting
        email_data = {
            "sender": "test@example.com",
            "subject": "Test Email",
            "body": "This is a test"
        }
        formatted = pm.format_prompt("categorization", email_data)
        assert "test@example.com" in formatted and "Test Email" in formatted, "Prompt formatting failed"
        
        print("✅ Prompt Manager working")
        return True
    except Exception as e:
        print(f"❌ Prompt Manager failed: {e}")
        return False


def test_mock_inbox():
    """Test mock inbox loading"""
    print("\nTesting Mock Inbox...")
    try:
        import json
        
        with open('data/mock_inbox.json', 'r', encoding='utf-8') as f:
            inbox = json.load(f)
        
        assert len(inbox) > 0, "Empty inbox"
        assert "id" in inbox[0], "Missing email ID"
        assert "sender" in inbox[0], "Missing sender"
        
        print(f"✅ Mock Inbox loaded: {len(inbox)} emails")
        return True
    except Exception as e:
        print(f"❌ Mock Inbox failed: {e}")
        return False


def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting File Structure...")
    
    required_files = [
        "app.py",
        "requirements.txt",
        "data/mock_inbox.json",
        "data/default_prompts.json",
        "src/__init__.py",
        "src/llm_client.py",
        "src/prompt_manager.py",
        "src/email_processor.py",
        "src/draft_manager.py",
        "src/email_agent.py",
        "README.md"
    ]
    
    all_exist = True
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"  ✅ {filepath}")
        else:
            print(f"  ❌ {filepath} - MISSING")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests"""
    print("="*50)
    print("Email Productivity Agent - Component Tests")
    print("="*50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_prompt_manager,
        test_mock_inbox
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*50)
    print(f"Tests Passed: {sum(results)}/{len(results)}")
    print("="*50)
    
    if all(results):
        print("\n🎉 All tests passed! Ready to run the application.")
        print("\nRun with: streamlit run app.py")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
