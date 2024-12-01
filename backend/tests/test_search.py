import pytest
import requests


def test_blah():
    
    return True

def test_search():
    url = "http://localhost:8000/search/"
    payload = {
        "query": "test search query"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()
        print("Response:", result)
        
        # Add some basic assertions
        assert response.status_code == 200
        assert isinstance(result, dict)
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 