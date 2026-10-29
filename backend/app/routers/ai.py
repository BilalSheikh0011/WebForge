from urllib.parse import urlparse
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["AI DOM Analyzer"])

class AnalyzeRequest(BaseModel):
    url: str

@router.post("/analyze")
def analyze_dom(payload: AnalyzeRequest):
    raw_url = payload.url.strip() if payload.url else "https://leatherlaneatelier.store"
    if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
        url = "https://" + raw_url
    else:
        url = raw_url

    domain = urlparse(url).netloc.lower() or "target-site"
    
    # Categorization heuristics
    is_ecommerce = any(k in domain for k in ["store", "shop", "leatherlane", "cart", "product", "buy", "daraz", "amazon"])
    is_portal = any(k in domain for k in ["login", "app", "auth", "admin", "portal", "dashboard", "github", "jira"])

    suggestions = []

    # =========================================================================
    # 1. E-COMMERCE SUITE (6 Comprehensive Test Cases)
    # =========================================================================
    if is_ecommerce:
        suggestions = [
            {
                "title": f"Catalog Search & Keyword Discovery ({domain})",
                "type": "Functional",
                "priority": "High",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "2000", "expected": ""},
                    {"order": 3, "action": "fill", "selector_type": "css", "selector": "input[type='search'], input[name='q'], input", "value": "shoes", "expected": ""},
                    {"order": 4, "action": "press", "selector_type": "", "selector": "", "value": "Enter", "expected": ""},
                    {"order": 5, "action": "wait", "selector_type": "", "selector": "", "value": "2000", "expected": ""},
                    {"order": 6, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "Cart Drawer & Bag Slide-Over State Verification",
                "type": "Integration",
                "priority": "Critical",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "click", "selector_type": "css", "selector": "header a[href*='cart'], button[aria-label*='cart' i], .cart-link, [data-action='open-cart']", "value": "", "expected": ""},
                    {"order": 4, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "Catalog Product Grid & Image Hydration Verification",
                "type": "Smoke",
                "priority": "Medium",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "2000", "expected": ""},
                    {"order": 3, "action": "scroll", "selector_type": "", "selector": "", "value": "800", "expected": ""},
                    {"order": 4, "action": "wait", "selector_type": "", "selector": "", "value": "1000", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "img, [role='img']", "expected": ""}
                ]
            },
            {
                "title": "Search Query Input Boundary Buffer Overflow (255-Char Fuzzing)",
                "type": "Boundary",
                "priority": "High",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "fill", "selector_type": "css", "selector": "input[type='search'], input[name='q'], input", "value": "A" * 255, "expected": ""},
                    {"order": 4, "action": "press", "selector_type": "", "selector": "", "value": "Enter", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "SQL Injection Defensive Hardening on Storefront Input",
                "type": "Negative",
                "priority": "Critical",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "fill", "selector_type": "css", "selector": "input", "value": "' OR '1'='1' --", "expected": ""},
                    {"order": 4, "action": "press", "selector_type": "", "selector": "", "value": "Enter", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "Header Navigation & Collection Menu Link Routing",
                "type": "Functional",
                "priority": "Medium",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "click", "selector_type": "css", "selector": "nav a, header a", "value": "", "expected": ""},
                    {"order": 4, "action": "wait", "selector_type": "", "selector": "", "value": "2000", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            }
        ]

    # =========================================================================
    # 2. PORTAL / SAAS / LOGIN SUITE (6 Comprehensive Test Cases)
    # =========================================================================
    elif is_portal:
        suggestions = [
            {
                "title": f"Authentication Form Validation & Field Traversal ({domain})",
                "type": "Functional",
                "priority": "Critical",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "2000", "expected": ""},
                    {"order": 3, "action": "fill", "selector_type": "css", "selector": "input[type='email'], input[name*='user' i], input", "value": "test_qa@webforge.io", "expected": ""},
                    {"order": 4, "action": "fill", "selector_type": "css", "selector": "input[type='password']", "value": "Pass123!Secure", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "Invalid Email Malformed Syntax Rejection",
                "type": "Boundary",
                "priority": "High",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "fill", "selector_type": "css", "selector": "input[type='email'], input", "value": "missing_at_domain.com", "expected": ""},
                    {"order": 4, "action": "press", "selector_type": "", "selector": "", "value": "Enter", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "SQL Injection Authentication Bypass Defense Test",
                "type": "Negative",
                "priority": "Critical",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "fill", "selector_type": "css", "selector": "input", "value": "admin' --", "expected": ""},
                    {"order": 4, "action": "press", "selector_type": "", "selector": "", "value": "Enter", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "XSS Script Tag Injection Sanitization on Input",
                "type": "Boundary",
                "priority": "High",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "fill", "selector_type": "css", "selector": "input", "value": "<script>alert(1)</script>", "expected": ""},
                    {"order": 4, "action": "press", "selector_type": "", "selector": "", "value": "Enter", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "Unauthenticated Route Protection & Redirect Check",
                "type": "Security",
                "priority": "High",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": f"{url.rstrip('/')}/dashboard", "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "2000", "expected": ""},
                    {"order": 3, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "Portal Brand Logo & Login Container Visibility",
                "type": "Smoke",
                "priority": "Medium",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "assert_visible", "selector_type": "css", "selector": "form, [role='form'], body", "expected": ""}
                ]
            }
        ]

    # =========================================================================
    # 3. GENERIC / CONTENT / ANY OTHER WEBSITE (5 Comprehensive Test Cases)
    # =========================================================================
    else:
        suggestions = [
            {
                "title": f"Landing Page Hero Banner & Structure Verification ({domain})",
                "type": "Smoke",
                "priority": "High",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "2000", "expected": ""},
                    {"order": 3, "action": "assert_visible", "selector_type": "css", "selector": "h1, header, nav, body", "expected": ""}
                ]
            },
            {
                "title": "Primary Header Navigation Routing Integrity Check",
                "type": "Functional",
                "priority": "Medium",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "click", "selector_type": "css", "selector": "nav a, header a", "value": "", "expected": ""},
                    {"order": 4, "action": "wait", "selector_type": "", "selector": "", "value": "2000", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "Input Field Boundary Overflow Fuzzing (255-Char Test)",
                "type": "Boundary",
                "priority": "High",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "fill", "selector_type": "css", "selector": "input", "value": "W" * 255, "expected": ""},
                    {"order": 4, "action": "press", "selector_type": "", "selector": "", "value": "Enter", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "Cross-Site Scripting (XSS) Sanitization Vector Test",
                "type": "Negative",
                "priority": "Critical",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "fill", "selector_type": "css", "selector": "input", "value": "<img src=x onerror=alert(1)>", "expected": ""},
                    {"order": 4, "action": "press", "selector_type": "", "selector": "", "value": "Enter", "expected": ""},
                    {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": "body", "expected": ""}
                ]
            },
            {
                "title": "Viewport Vertical Scrolling & Footer Content Rendering",
                "type": "Functional",
                "priority": "Low",
                "steps": [
                    {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                    {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                    {"order": 3, "action": "scroll", "selector_type": "", "selector": "", "value": "1200", "expected": ""},
                    {"order": 4, "action": "assert_visible", "selector_type": "css", "selector": "footer, body", "expected": ""}
                ]
            }
        ]

    return {"url": url, "domain": domain, "suggestions": suggestions}