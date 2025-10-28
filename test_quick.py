#!/usr/bin/env python3
"""
Test rápido del ML Service con datos bolivianos
"""
import requests
import json

def test_health():
    """Test health check"""
    print("🏥 Testing Health Check...")
    r = requests.get('http://localhost:5015/health')
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
    return r.status_code == 200

def test_bolivian_classification():
    """Test clasificación boliviana"""
    print("\n🇧🇴 Testing Bolivian Transaction Classification...")
    
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
    
    try:
        r = requests.post(
            'http://localhost:5015/graphql', 
            json={'query': query}, 
            headers={'user-id': '550e8400-e29b-41d4-a716-446655440000'},  # UUID válido
            timeout=10
        )
        
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            result = r.json()
            
            if 'data' in result and result['data']['classifyTransaction']:
                data = result['data']['classifyTransaction']
                print(f"✅ Category: {data['predictedCategory']}")
                print(f"✅ Confidence: {data['confidence']:.1%}")
                
                if data['alternativeCategories']:
                    print("📊 Alternatives:")
                    for alt in data['alternativeCategories'][:3]:
                        print(f"   - {alt['category']}: {alt['confidence']:.1%}")
                
                return True
            else:
                print(f"❌ Error in response: {result}")
                return False
        else:
            print(f"❌ HTTP Error: {r.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_multiple_bolivian_merchants():
    """Test múltiples comercios bolivianos"""
    print("\n🏪 Testing Multiple Bolivian Merchants...")
    
    merchants = [
        "HIPERMAXI ZONA SUR",
        "FARMACIA CHAVEZ MEDICAMENTOS",
        "TAXI LA PAZ SOPOCACHI",
        "TELEFERICO ROJO BOLETO"
    ]
    
    query_template = """
    mutation {{
        classifyTransaction(input: {{
            text: "{merchant}"
        }}) {{
            predictedCategory
            confidence
        }}
    }}
    """
    
    results = []
    
    for merchant in merchants:
        try:
            query = query_template.format(merchant=merchant)
            r = requests.post(
                'http://localhost:5015/graphql',
                json={'query': query},
                headers={'user-id': '550e8400-e29b-41d4-a716-446655440000'},  # UUID válido
                timeout=10
            )
            
            if r.status_code == 200:
                result = r.json()
                if 'data' in result and result['data']['classifyTransaction']:
                    data = result['data']['classifyTransaction']
                    results.append({
                        'merchant': merchant,
                        'category': data['predictedCategory'],
                        'confidence': data['confidence']
                    })
                    print(f"✅ {merchant[:25]:<25} → {data['predictedCategory']:<15} ({data['confidence']:.1%})")
                else:
                    print(f"❌ {merchant}: Error in response")
            else:
                print(f"❌ {merchant}: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"❌ {merchant}: {e}")
    
    return len(results) > 0

def main():
    """Ejecutar todos los tests"""
    print("🧪 ML Service - Test Boliviano Rápido")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Bolivian Classification", test_bolivian_classification), 
        ("Multiple Merchants", test_multiple_bolivian_merchants)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{'▶' * 3} {name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {name} PASSED")
            else:
                print(f"❌ {name} FAILED")
        except Exception as e:
            print(f"❌ {name} ERROR: {e}")
    
    print(f"\n{'=' * 50}")
    print(f"🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron!")
        print("🇧🇴 ML Service funciona perfectamente con datos bolivianos!")
    else:
        print("⚠️  Algunos tests fallaron, revisar logs arriba")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
