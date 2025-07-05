#!/usr/bin/env python3
"""
Test script for the chatbot API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_get_contexts():
    """Test getting available contexts"""
    try:
        response = requests.get(f"{BASE_URL}/chatbot/context")
        print(f"✅ Get contexts: {response.status_code}")
        print(f"Available contexts: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Get contexts failed: {e}")
        return False

def test_chat_history():
    """Test getting chat history"""
    try:
        user_id = "test_user_123"
        response = requests.get(f"{BASE_URL}/chatbot/{user_id}")
        print(f"✅ Get chat history: {response.status_code}")
        print(f"Chat history: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Get chat history failed: {e}")
        return False

def test_process_message():
    """Test processing a message"""
    try:
        user_id = "test_user_123"
        data = {
            "query": "Hello! How are you?",
            "context": None  # Regular chat
        }
        response = requests.post(f"{BASE_URL}/chatbot/{user_id}", json=data)
        print(f"✅ Process message (regular): {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test with RAG context
        data = {
            "query": "Tell me about Suhas",
            "context": "suhas_profile_chunks"
        }
        response = requests.post(f"{BASE_URL}/chatbot/{user_id}", json=data)
        print(f"✅ Process message (RAG): {response.status_code}")
        print(f"Response: {response.json()}")
        
        return True
    except Exception as e:
        print(f"❌ Process message failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Chatbot API Endpoints")
    print("=" * 40)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(5)
    
    tests = [
        ("Health Check", test_health),
        ("Get Contexts", test_get_contexts),
        ("Get Chat History", test_chat_history),
        ("Process Message", test_process_message),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📝 Testing: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results:")
    print("=" * 40)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed")

if __name__ == "__main__":
    main() 