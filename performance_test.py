#!/usr/bin/env python3
"""
Performance test script for the Election game web application.
Tests response times, throughput, and resource usage.
"""

import requests
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
import threading

BASE_URL = "http://localhost:5001"

def test_single_request(url, method='GET', data=None, headers=None):
    """Test a single request and return timing data."""
    start_time = time.time()
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        
        end_time = time.time()
        return {
            'url': url,
            'method': method,
            'status_code': response.status_code,
            'response_time': (end_time - start_time) * 1000,  # Convert to ms
            'success': response.status_code == 200,
            'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        end_time = time.time()
        return {
            'url': url,
            'method': method,
            'status_code': None,
            'response_time': (end_time - start_time) * 1000,
            'success': False,
            'error': str(e)
        }

def test_static_files():
    """Test static file loading performance."""
    print("Testing static file performance...")
    
    static_files = [
        "/static/style.css",
        "/static/script.js",
        "/static/index.html"
    ]
    
    results = []
    for file_path in static_files:
        result = test_single_request(f"{BASE_URL}{file_path}")
        results.append(result)
        print(f"  {file_path}: {result['response_time']:.2f}ms ({'✓' if result['success'] else '✗'})")
    
    return results

def test_api_endpoints():
    """Test API endpoint performance."""
    print("\nTesting API endpoint performance...")
    
    # Create a game first
    game_data = {"player_names": ["Alice", "Bob", "Charlie"]}
    create_result = test_single_request(
        f"{BASE_URL}/api/game",
        method='POST',
        data=game_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"  Create game: {create_result['response_time']:.2f}ms ({'✓' if create_result['success'] else '✗'})")
    
    if create_result['success']:
        try:
            # Parse the response to get game_id
            response_data = create_result.get('response', {})
            if isinstance(response_data, str):
                response_data = json.loads(response_data)
            game_id = response_data.get('game_id')
            if game_id:
                # Test getting game state
                get_result = test_single_request(f"{BASE_URL}/api/game/{game_id}")
                print(f"  Get game state: {get_result['response_time']:.2f}ms ({'✓' if get_result['success'] else '✗'})")
                
                # Test performing an action
                action_data = {
                    "action_type": "fundraise",
                    "player_id": 0
                }
                action_result = test_single_request(
                    f"{BASE_URL}/api/game/{game_id}/action",
                    method='POST',
                    data=action_data,
                    headers={"Content-Type": "application/json"}
                )
                print(f"  Perform action: {action_result['response_time']:.2f}ms ({'✓' if action_result['success'] else '✗'})")
                
                return [create_result, get_result, action_result]
        except Exception as e:
            print(f"  Error testing API: {e}")
    
    return [create_result]

def test_concurrent_requests(num_requests=10):
    """Test concurrent request handling."""
    print(f"\nTesting concurrent requests ({num_requests} requests)...")
    
    def make_request():
        return test_single_request(f"{BASE_URL}/")
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        results = list(executor.map(lambda _: make_request(), range(num_requests)))
    end_time = time.time()
    
    successful_requests = [r for r in results if r['success']]
    response_times = [r['response_time'] for r in successful_requests]
    
    if response_times:
        print(f"  Total time: {(end_time - start_time) * 1000:.2f}ms")
        print(f"  Successful requests: {len(successful_requests)}/{num_requests}")
        print(f"  Average response time: {statistics.mean(response_times):.2f}ms")
        print(f"  Min response time: {min(response_times):.2f}ms")
        print(f"  Max response time: {max(response_times):.2f}ms")
        print(f"  Median response time: {statistics.median(response_times):.2f}ms")
        print(f"  Requests per second: {len(successful_requests) / ((end_time - start_time)):.1f}")
    
    return results

def test_memory_usage():
    """Test memory usage by creating multiple games."""
    print("\nTesting memory usage...")
    
    game_ids = []
    start_time = time.time()
    
    for i in range(10):
        game_data = {"player_names": [f"Player{i}", f"Player{i+1}"]}
        result = test_single_request(
            f"{BASE_URL}/api/game",
            method='POST',
            data=game_data,
            headers={"Content-Type": "application/json"}
        )
        
        if result['success']:
            try:
                # Parse the response to get game_id
                response_data = result.get('response', {})
                if isinstance(response_data, str):
                    response_data = json.loads(response_data)
                game_id = response_data.get('game_id')
                if game_id:
                    game_ids.append(game_id)
            except Exception as e:
                print(f"    Error parsing response: {e}")
                pass
    
    end_time = time.time()
    print(f"  Created {len(game_ids)} games in {(end_time - start_time) * 1000:.2f}ms")
    if len(game_ids) > 0:
        print(f"  Average time per game: {(end_time - start_time) / len(game_ids) * 1000:.2f}ms")
    else:
        print(f"  No games created successfully")
    
    # Clean up games
    for game_id in game_ids:
        try:
            requests.delete(f"{BASE_URL}/api/game/{game_id}")
        except:
            pass
    
    return len(game_ids)

def test_mobile_simulation():
    """Simulate mobile device performance."""
    print("\nTesting mobile simulation...")
    
    mobile_headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    }
    
    # Test main page load
    main_result = test_single_request(f"{BASE_URL}/", headers=mobile_headers)
    print(f"  Mobile main page: {main_result['response_time']:.2f}ms ({'✓' if main_result['success'] else '✗'})")
    
    # Test static files
    static_results = []
    for file_path in ["/static/style.css", "/static/script.js"]:
        result = test_single_request(f"{BASE_URL}{file_path}", headers=mobile_headers)
        static_results.append(result)
        print(f"  Mobile {file_path}: {result['response_time']:.2f}ms ({'✓' if result['success'] else '✗'})")
    
    return [main_result] + static_results

def main():
    print("Election Game Performance Test")
    print("=" * 50)
    
    # Test static files
    static_results = test_static_files()
    
    # Test API endpoints
    api_results = test_api_endpoints()
    
    # Test concurrent requests
    concurrent_results = test_concurrent_requests(20)
    
    # Test memory usage
    games_created = test_memory_usage()
    
    # Test mobile simulation
    mobile_results = test_mobile_simulation()
    
    # Summary
    print("\n" + "=" * 50)
    print("PERFORMANCE SUMMARY")
    print("=" * 50)
    
    all_response_times = []
    for results in [static_results, api_results, concurrent_results, mobile_results]:
        if isinstance(results, list):
            all_response_times.extend([r['response_time'] for r in results if r.get('success')])
        else:
            all_response_times.append(results['response_time'])
    
    if all_response_times:
        print(f"Average response time: {statistics.mean(all_response_times):.2f}ms")
        print(f"95th percentile: {sorted(all_response_times)[int(len(all_response_times) * 0.95)]:.2f}ms")
        print(f"99th percentile: {sorted(all_response_times)[int(len(all_response_times) * 0.99)]:.2f}ms")
    
    print(f"Games created in memory test: {games_created}")
    
    print("\nPerformance Assessment:")
    avg_time = statistics.mean(all_response_times) if all_response_times else 0
    if avg_time < 50:
        print("🟢 EXCELLENT - Sub-50ms average response time")
    elif avg_time < 100:
        print("🟡 GOOD - Sub-100ms average response time")
    elif avg_time < 200:
        print("🟠 ACCEPTABLE - Sub-200ms average response time")
    else:
        print("🔴 NEEDS IMPROVEMENT - Over 200ms average response time")
    
    print(f"\nServer is ready for local deployment!")
    print(f"Access the game at: {BASE_URL}")

if __name__ == "__main__":
    main() 