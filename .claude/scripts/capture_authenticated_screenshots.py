#!/usr/bin/env python3
"""
Screenshot Capture Script for TidySnap Flutter Web App

This script automatically:
1. Finds the running Flutter app port
2. Reads test credentials from .env
3. Logs in to the app
4. Captures screenshots of authenticated pages
5. Saves screenshots to review_screenshots/

Usage:
    python3 .claude/scripts/capture_authenticated_screenshots.py

Requirements:
    - Flutter app must be running (flutter run -d chrome)
    - Playwright must be installed (pip install playwright && playwright install chromium)
    - .env file must contain TEST_EMAIL and TEST_PASSWORD
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def read_env():
    """Read environment variables from .env file"""
    env_vars = {}
    env_path = Path('.env')

    if not env_path.exists():
        print("❌ ERROR: .env file not found")
        return None

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key] = value

    return env_vars


def find_flutter_port():
    """Find the port of running Flutter web app"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)

        # Look for flutter run process with port
        port_match = re.search(r'localhost:(\d+)', result.stdout)
        if port_match:
            return port_match.group(1)

        # Try common ports
        for port in ['45419', '8080', '3000', '5000']:
            test_result = subprocess.run(
                ['curl', '-s', f'http://localhost:{port}'],
                capture_output=True,
                timeout=2
            )
            if test_result.returncode == 0:
                return port

        return None
    except Exception as e:
        print(f"❌ Error finding port: {e}")
        return None


def capture_screenshots(url, test_email, test_password, output_dir='review_screenshots'):
    """Capture authenticated screenshots using Playwright"""

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    print(f"📸 Starting screenshot capture...")
    print(f"   URL: {url}")
    print(f"   Email: {test_email}")
    print(f"   Output: {output_dir}/")

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to app
            print(f"\n1️⃣ Loading app at {url}...")
            page.goto(url, timeout=30000)
            page.wait_for_load_state('networkidle', timeout=15000)

            # Screenshot 1: Login screen
            login_screenshot = f'{output_dir}/01_login_screen.png'
            page.screenshot(path=login_screenshot)
            print(f"   ✅ Captured: {login_screenshot}")

            # Try to login
            print(f"\n2️⃣ Attempting login with {test_email}...")

            try:
                # Find and fill email field
                page.fill('input[type="email"]', test_email)
                print(f"   ✓ Filled email")

                # Find and fill password field
                page.fill('input[type="password"]', test_password)
                print(f"   ✓ Filled password")

                # Click login button
                page.click('button[type="submit"]')
                print(f"   ✓ Clicked login button")

                # Wait for navigation to home/dashboard
                print(f"   ⏳ Waiting for navigation...")
                page.wait_for_url('**/home', timeout=15000)
                page.wait_for_load_state('networkidle', timeout=10000)

                # Screenshot 2: Authenticated dashboard
                dashboard_screenshot = f'{output_dir}/02_dashboard_authenticated.png'
                page.screenshot(path=dashboard_screenshot)
                print(f"   ✅ Captured: {dashboard_screenshot}")

                # Screenshot 3: Full page (if needed)
                fullpage_screenshot = f'{output_dir}/03_dashboard_fullpage.png'
                page.screenshot(path=fullpage_screenshot, full_page=True)
                print(f"   ✅ Captured: {fullpage_screenshot}")

                print(f"\n✅ SUCCESS: All screenshots captured!")
                return True

            except PlaywrightTimeoutError as e:
                print(f"\n⚠️  Login timeout: {e}")
                print(f"   Only login screen captured")
                return False

            except Exception as e:
                print(f"\n❌ Login failed: {e}")
                print(f"   Only login screen captured")
                return False

        finally:
            browser.close()


def main():
    """Main execution"""
    print("="*60)
    print("🎬 TidySnap Screenshot Capture Tool")
    print("="*60)

    # Read .env
    print("\n📋 Reading .env file...")
    env_vars = read_env()
    if not env_vars:
        sys.exit(1)

    test_email = env_vars.get('TEST_EMAIL')
    test_password = env_vars.get('TEST_PASSWORD')

    if not test_email or not test_password:
        print("❌ ERROR: TEST_EMAIL or TEST_PASSWORD not found in .env")
        sys.exit(1)

    print(f"   ✓ TEST_EMAIL: {test_email}")
    print(f"   ✓ TEST_PASSWORD: {'*' * len(test_password)}")

    # Find Flutter port
    print("\n🔍 Finding Flutter app...")
    port = find_flutter_port()
    if not port:
        print("❌ ERROR: Cannot find running Flutter app")
        print("   Make sure Flutter app is running: flutter run -d chrome --release")
        sys.exit(1)

    url = f'http://localhost:{port}'
    print(f"   ✓ Found app at: {url}")

    # Capture screenshots
    success = capture_screenshots(url, test_email, test_password)

    # Summary
    print("\n" + "="*60)
    if success:
        print("✅ COMPLETE: Screenshots saved to review_screenshots/")
        print("\nNext steps:")
        print("   1. Review screenshots: ls -lh review_screenshots/")
        print("   2. Run spec-implementation-reviewer agent")
    else:
        print("⚠️  PARTIAL: Only login screen captured")
        print("\nTroubleshooting:")
        print("   - Check if test credentials are correct in .env")
        print("   - Check if app login flow has changed")
        print("   - Try manual login to verify credentials")
    print("="*60)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
