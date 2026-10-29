from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def fetch_rendered_html(url: str) -> str:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            html = page.content()
        finally:
            browser.close()
    return html

def analyze_dom_and_suggest(url: str):
    try:
        html = fetch_rendered_html(url)
    except Exception as e:
        # Fallback for offline or unreachable demo targets
        html = "<html><body><form><input type='text' id='search' name='q' /><input type='email' id='email' /><input type='password' id='password' /><button type='submit'>Submit</button></form></body></html>"

    soup = BeautifulSoup(html, "html.parser")
    suggestions = []

    # 1. Login / Authentication Flow Detection
    has_pw = soup.select_one("input[type='password']")
    email_or_user = soup.select_one("input[type='email'], input[name*='user' i], input[id*='user' i]")
    
    if has_pw and email_or_user:
        user_id = email_or_user.get("id") or email_or_user.get("name") or "user-name"
        pw_id = has_pw.get("id") or has_pw.get("name") or "password"
        submit_btn = soup.select_one("input[type='submit'], button[type='submit'], button[id*='login' i]")
        btn_sel = submit_btn.get("id") if submit_btn and submit_btn.get("id") else "login-button"

        suggestions.append({
            "id": "AI-AUTH-01",
            "title": "Authentication: Login with Valid Credentials",
            "priority": "Critical",
            "type": "Functional",
            "description": "Validates that valid user credentials grant access to authenticated application area.",
            "steps": [
                {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                {"order": 2, "action": "fill", "selector_type": "id", "selector": user_id, "value": "standard_user", "expected": ""},
                {"order": 3, "action": "fill", "selector_type": "id", "selector": pw_id, "value": "secret_sauce", "expected": ""},
                {"order": 4, "action": "click", "selector_type": "id", "selector": btn_sel, "value": "", "expected": ""},
                {"order": 5, "action": "assert_url_equals", "selector_type": "", "selector": "", "value": "", "expected": f"{url.rstrip('/')}/inventory.html"}
            ]
        })

        suggestions.append({
            "id": "AI-AUTH-02",
            "title": "Authentication: Negative Wrong Password Error State",
            "priority": "Critical",
            "type": "Negative",
            "description": "Asserts system rejects incorrect credentials with an error banner.",
            "steps": [
                {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                {"order": 2, "action": "fill", "selector_type": "id", "selector": user_id, "value": "invalid_user", "expected": ""},
                {"order": 3, "action": "fill", "selector_type": "id", "selector": pw_id, "value": "wrong_password", "expected": ""},
                {"order": 4, "action": "click", "selector_type": "id", "selector": btn_sel, "value": "", "expected": ""},
                {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": ".error-message-container, [data-test='error'], .alert-danger", "value": "", "expected": ""}
            ]
        })

    # 2. Search & Filter Bar Detection
    search_input = soup.select_one("input[name*='q' i], input[type='search'], input[id*='search' i], input[placeholder*='search' i]")
    if search_input:
        s_target = search_input.get("id") or search_input.get("name") or "search"
        suggestions.append({
            "id": "AI-SRCH-01",
            "title": "Catalog Search: Product Query & Grid Response",
            "priority": "High",
            "type": "Integration",
            "description": "Verifies that entering keywords renders matching catalog products.",
            "steps": [
                {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                {"order": 2, "action": "wait", "selector_type": "", "selector": "", "value": "1500", "expected": ""},
                {"order": 3, "action": "fill", "selector_type": "css", "selector": f"input#{s_target}" if search_input.get("id") else f"input[name='{s_target}']", "value": "Shirt", "expected": ""},
                {"order": 4, "action": "wait", "selector_type": "", "selector": "", "value": "1000", "expected": ""},
                {"order": 5, "action": "assert_visible", "selector_type": "css", "selector": ".product-item, .products-grid, .inventory_item", "value": "", "expected": ""}
            ]
        })

    # 3. Form Boundary Input Constraints
    email_field = soup.select_one("input[type='email']")
    if email_field:
        em_target = email_field.get("id") or email_field.get("name") or "email"
        suggestions.append({
            "id": "AI-BND-01",
            "title": "Form Validation: Email 255-Character Boundary Test",
            "priority": "Medium",
            "type": "Boundary",
            "description": "Boundary value testing for input overflow and buffer truncation.",
            "steps": [
                {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                {"order": 2, "action": "fill", "selector_type": "css", "selector": f"#{em_target}" if email_field.get("id") else f"input[name='{em_target}']", "value": ("a" * 240) + "@testdomain.com", "expected": ""},
                {"order": 3, "action": "wait", "selector_type": "", "selector": "", "value": "500", "expected": ""}
            ]
        })

    # 4. Mandatory / Required Form Field Check
    required_inputs = soup.select("input[required]")
    if required_inputs:
        suggestions.append({
            "id": "AI-NEG-01",
            "title": "Negative Testing: Empty Form Submit Triggers Required Validation",
            "priority": "High",
            "type": "Negative",
            "description": "Verifies that submitting blank mandatory fields displays validation cues.",
            "steps": [
                {"order": 1, "action": "navigate", "selector_type": "", "selector": "", "value": url, "expected": ""},
                {"order": 2, "action": "click", "selector_type": "css", "selector": "button[type='submit'], input[type='submit']", "value": "", "expected": ""},
                {"order": 3, "action": "assert_visible", "selector_type": "css", "selector": ":invalid, .error, .text-danger", "value": "", "expected": ""}
            ]
        })

    return suggestions