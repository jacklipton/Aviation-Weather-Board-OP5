
import requests
import time
import sys

BASE_URL = "http://localhost:8080"

def test_brightness():
    # 1. Check initial status
    print("Checking initial status...")
    try:
        r = requests.get(f"{BASE_URL}/api/status")
        r.raise_for_status()
        status = r.json()
        print(f"Initial Status: {status}")
        initial_brightness = status.get("brightness")
        if initial_brightness is None:
            print("❌ FAIL: 'brightness' not in status response")
            sys.exit(1)
    except Exception as e:
        print(f"❌ FAIL: Could not fetch status: {e}")
        sys.exit(1)

    # 2. Set brightness to 128
    print("\nSetting brightness to 128...")
    try:
        r = requests.post(f"{BASE_URL}/api/control/brightness", json={"brightness": 128})
        r.raise_for_status()
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"❌ FAIL: Could not set brightness: {e}")
        sys.exit(1)

    # 3. Verify status updated
    print("\nVerifying status...")
    try:
        r = requests.get(f"{BASE_URL}/api/status")
        r.raise_for_status()
        status = r.json()
        print(f"New Status: {status}")
        if status["brightness"] == 128:
            print("✅ PASS: Brightness updated correctly")
        else:
            print(f"❌ FAIL: Expected 128, got {status['brightness']}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ FAIL: Could not fetch status: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Wait a bit for server to start if running immediately after startup
    time.sleep(2)
    test_brightness()
