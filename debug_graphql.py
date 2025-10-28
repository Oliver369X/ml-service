#!/usr/bin/env python3
"""
Debug GraphQL response
"""
import requests
import json

def debug_graphql():
    query = """
    mutation {
        classifyTransaction(input: {
            text: "KETAL SUPERMERCADO MIRAFLORES"
        }) {
            predictedCategory
            confidence
            alternativeCategories {
                category
                confidence
            }
        }
    }
    """
    
    print("🔍 Debug GraphQL Response...")
    
    r = requests.post(
        'http://localhost:5015/graphql', 
        json={'query': query}, 
        headers={'user-id': '550e8400-e29b-41d4-a716-446655440000'},  # UUID válido
        timeout=10
    )
    
    print(f"Status Code: {r.status_code}")
    print(f"Headers: {dict(r.headers)}")
    
    try:
        response_json = r.json()
        print("Full Response:")
        print(json.dumps(response_json, indent=2))
        
        if 'errors' in response_json:
            print("\n❌ GraphQL Errors:")
            for error in response_json['errors']:
                print(f"  - {error}")
        
        if 'data' in response_json:
            print(f"\n📦 Data: {response_json['data']}")
            
            if response_json['data'] and 'classifyTransaction' in response_json['data']:
                result = response_json['data']['classifyTransaction'] 
                if result:
                    print(f"✅ Transaction Result: {result}")
                else:
                    print("❌ classifyTransaction is null/None")
            else:
                print("❌ No classifyTransaction in data")
    except Exception as e:
        print(f"❌ Error parsing JSON: {e}")
        print(f"Raw response: {r.text}")

if __name__ == '__main__':
    debug_graphql()
