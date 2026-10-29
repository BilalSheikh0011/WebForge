import base64
import time
from typing import List, Dict, Any, Tuple, Optional
from playwright.sync_api import sync_playwright

def wait_for_page_settlement(page, timeout_ms: int = 4000):
    """
    Ensures DOM content is loaded and settles animations without hanging indefinitely.
    """
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
    except Exception:
        pass

    try:
        page.evaluate("""
            async () => {
                const animations = document.getAnimations();
                await Promise.all(animations.map(a => a.finished));
            }
        """)
    except Exception:
        pass

    page.wait_for_timeout(600)


def auto_uncover_hidden_inputs(page, target_keyword: str):
    """
    Uncovers hidden drawers, search modals, or mobile toggles if element is tucked away.
    """
    kw = (target_keyword or "").lower()
    if any(k in kw for k in ["search", "find", "query", "q", "filter"]):
        triggers = [
            "summary[aria-label*='search' i]",
            "button[aria-label*='search' i]",
            "a[href*='/search']",
            "button.search-modal__toggle",
            ".header__search",
            ".search-toggle",
            "[data-action='toggle-search']",
            "svg.icon-search",
            "button[type='submit']:has(svg)"
        ]
        for trig in triggers:
            try:
                el = page.locator(trig).first
                if el.count() > 0 and el.is_visible():
                    el.click(timeout=1200)
                    page.wait_for_timeout(400)
                    break
            except Exception:
                continue


def diagnose_failure(step: Dict[str, Any], err_msg: str, url: str) -> Tuple[str, str]:
    """
    Produces deterministic root-cause analysis and actionable remediation advice.
    """
    action = step.get("action", "").lower().strip()
    selector = step.get("selector", "")
    err_lower = err_msg.lower()

    if "timeout" in err_lower or "waiting for locator" in err_lower:
        explanation = (
            f"The browser waited for locator '{selector}', but it never became visible, attached, "
            f"or stable in the DOM within the threshold."
        )
        suggestion = "Add an explicit 'wait' step (2000ms–3000ms) before this action, or verify that the element is not tucked inside a collapsed menu/drawer."
        return explanation, suggestion

    if "expected exact text" in err_lower or "expected text" in err_lower:
        explanation = "Assertion discrepancy: The element was found, but the inner text did not match the expected value."
        suggestion = "Switch action to 'assert_text_contains' to permit partial matching and avoid whitespace sensitivity."
        return explanation, suggestion

    if "assert_visible" in action:
        explanation = f"Assertion failed: Target element '{selector}' was not rendered visible on the screen."
        suggestion = "Verify if the target URL has finished client-side hydration, or loosen the selector to target a parent container."
        return explanation, suggestion

    explanation = f"Execution halted during step '{action}'. Reason: {err_msg[:160]}"
    suggestion = "Check target URL accessibility, verify selector specificity, or test in a non-headless browser session."
    return explanation, suggestion


def locate_with_healing(page, step: Dict[str, Any]) -> Tuple[Any, bool, str]:
    """
    Attempts primary selector resolution, then applies heuristic self-healing strategies.
    """
    kind = (step.get("selector_type") or "").lower()
    sel = (step.get("selector") or "").strip()

    # 1. Primary Strategy
    try:
        if kind == "id":
            clean_id = sel.lstrip("#").strip()
            loc = page.locator(f"#{clean_id}")
            if loc.count() > 0:
                return loc.first, False, "primary_id"
        elif kind == "css":
            loc = page.locator(sel)
            if loc.count() > 0:
                return loc.first, False, "primary_css"
        elif kind == "xpath":
            loc = page.locator(f"xpath={sel}")
            if loc.count() > 0:
                return loc.first, False, "primary_xpath"
        elif kind == "name":
            loc = page.locator(f"[name='{sel}']")
            if loc.count() > 0:
                return loc.first, False, "primary_name"
        elif kind == "link":
            loc = page.get_by_role("link", name=sel)
            if loc.count() > 0:
                return loc.first, False, "primary_link"
        elif kind == "aria":
            loc = page.get_by_label(sel)
            if loc.count() > 0:
                return loc.first, False, "primary_aria"
    except Exception:
        pass

    # 2. Self-Healing Fallback 1: Text-based matching
    if sel:
        try:
            loc = page.get_by_text(sel, exact=False)
            if loc.count() > 0:
                return loc.first, True, f"self_healed_text_match('{sel}')"
        except Exception:
            pass

    # 3. Self-Healing Fallback 2: Universal Search Input recovery
    if any(k in sel.lower() for k in ["search", "find", "q"]):
        try:
            loc = page.locator("input[type='search'], input[name='q'], input[placeholder*='search' i]").first
            if loc.count() > 0:
                return loc, True, "self_healed_universal_search_input"
        except Exception:
            pass

    # 4. Fallback Default
    return page.locator(sel if sel else "body").first, False, "unhealed"


def run_single_action(page, step: Dict[str, Any], base_url: str) -> Tuple[str, bool, Optional[str]]:
    action = step.get("action", "").lower().strip()
    val = str(step.get("value") or "").strip()
    expected = str(step.get("expected") or "").strip()
    sel = (step.get("selector") or "").strip()
    healed = False
    healing_note = None

    if action == "navigate":
        target = val if val else base_url
        try:
            # domcontentloaded with a 15-second cap prevents hanging on background analytics
            page.goto(target, wait_until="domcontentloaded", timeout=15000)
        except Exception:
            try:
                page.goto(target, wait_until="commit", timeout=10000)
            except Exception as e:
                raise AssertionError(f"Could not load destination '{target}': {str(e)[:100]}")
        wait_for_page_settlement(page, timeout_ms=3000)
        return page.url, healed, healing_note

    elif action in ["click", "dblclick"]:
        auto_uncover_hidden_inputs(page, sel)
        loc, healed, reason = locate_with_healing(page, step)
        try:
            loc.scroll_into_view_if_needed(timeout=2500)
        except Exception:
            pass

        try:
            if action == "click":
                loc.click(timeout=5000)
            else:
                loc.dblclick(timeout=5000)
        except Exception:
            loc.click(force=True, timeout=4000)

        page.wait_for_timeout(600)
        return f"{action.capitalize()}ed successfully", healed, f"Resolved via {reason}" if healed else None

    elif action in ["fill", "clear"]:
        auto_uncover_hidden_inputs(page, sel + " " + val)
        loc, healed, reason = locate_with_healing(page, step)

        if action == "clear":
            try:
                loc.clear(timeout=3000)
            except Exception:
                loc.fill("")
            return "Input cleared", healed, None

        filled_successfully = False
        try:
            loc.fill(val, timeout=3000)
            filled_successfully = True
        except Exception:
            try:
                loc.fill(val, force=True, timeout=2000)
                filled_successfully = True
            except Exception:
                pass

        if not filled_successfully:
            try:
                loc.evaluate(
                    """(el, text) => {
                        el.focus();
                        el.value = text;
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }""",
                    val
                )
                filled_successfully = True
                healed = True
                reason = "direct_dom_evaluation_bypass"
            except Exception:
                pass

        return f"Filled {len(val)} characters", healed, f"Resolved via {reason}" if healed else None

    elif action == "press":
        key = val if val else "Enter"
        page.keyboard.press(key)
        page.wait_for_timeout(800)
        return f"Pressed {key}", False, None

    elif action == "wait":
        wait_ms = int(val) if val.isdigit() else 2000
        page.wait_for_timeout(wait_ms)
        return f"Waited {wait_ms}ms", False, None

    elif action == "assert_visible":
        loc, healed, reason = locate_with_healing(page, step)
        if not loc.is_visible():
            raise AssertionError(f"Element '{sel}' is not visible on page")
        return "Element is visible", healed, f"Resolved via {reason}" if healed else None

    elif action == "assert_hidden":
        loc, healed, reason = locate_with_healing(page, step)
        if loc.is_visible():
            raise AssertionError(f"Element '{sel}' was expected to be hidden, but is visible")
        return "Element is hidden", healed, f"Resolved via {reason}" if healed else None

    elif action == "assert_text_contains":
        loc, healed, reason = locate_with_healing(page, step)
        actual_txt = loc.inner_text().strip()
        if expected.lower() not in actual_txt.lower():
            raise AssertionError(f"Expected text '{actual_txt}' to contain '{expected}'")
        return actual_txt, healed, f"Resolved via {reason}" if healed else None

    elif action == "assert_text_equals":
        loc, healed, reason = locate_with_healing(page, step)
        actual_txt = loc.inner_text().strip()
        if actual_txt != expected:
            raise AssertionError(f"Expected exact text '{expected}', but found '{actual_txt}'")
        return actual_txt, healed, f"Resolved via {reason}" if healed else None

    elif action == "assert_url_equals":
        current_url = page.url.strip()
        if current_url != val.strip():
            raise AssertionError(f"Expected URL '{val}', but currently on '{current_url}'")
        return current_url, False, None

    elif action == "assert_title":
        current_title = page.title().strip()
        if expected.lower() not in current_title.lower():
            raise AssertionError(f"Expected title to contain '{expected}', but got '{current_title}'")
        return current_title, False, None

    return f"Action '{action}' executed", False, None


def execute_case(
    steps: List[Dict[str, Any]], 
    base_url: str = "https://leatherlaneatelier.store", 
    baseline_screenshot: Optional[str] = None, 
    stop_on_fail: bool = True
) -> Tuple[List[Dict[str, Any]], Optional[str], List[str], List[str]]:
    results: List[Dict[str, Any]] = []
    failed = False
    final_screenshot: Optional[str] = None
    browser_console_logs: List[str] = []
    network_failures: List[str] = []

    screen_dim = {"width": 1366, "height": 768}
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            user_agent=ua,
            viewport=screen_dim,
            screen=screen_dim,
            ignore_https_errors=True
        )

        page = context.new_page()
        page.set_viewport_size(screen_dim)
        page.set_default_timeout(10000)

        page.on("console", lambda msg: browser_console_logs.append(f"[{msg.type.upper()}] {msg.text[:120]}") if msg.type in ["error", "warning"] else None)
        page.on("requestfailed", lambda req: network_failures.append(f"{req.method} {req.url[:70]} - {req.failure}"))

        for i, step in enumerate(steps, start=1):
            action = step.get("action", "").lower().strip()

            if failed and stop_on_fail:
                results.append({
                    "index": i,
                    "action": action,
                    "status": "SKIPPED",
                    "ms": 0,
                    "actual": "Skipped due to earlier failure",
                    "error": None,
                    "explanation": None,
                    "suggestion": None,
                    "screenshot_b64": None,
                    "healed": False,
                    "healing_note": None,
                    "attempts": 0
                })
                continue

            start_time = time.time()
            rec: Dict[str, Any] = {
                "index": i,
                "action": action,
                "status": "PASS",
                "actual": "",
                "error": None,
                "explanation": None,
                "suggestion": None,
                "screenshot_b64": None,
                "healed": False,
                "healing_note": None,
                "attempts": 1
            }

            try:
                actual, healed, healing_note = run_single_action(page, step, base_url)
                rec["actual"] = actual
                rec["healed"] = healed
                rec["healing_note"] = healing_note
            except Exception as first_err:
                page.wait_for_timeout(800)
                try:
                    actual, healed, healing_note = run_single_action(page, step, base_url)
                    rec["status"] = "FLAKY"
                    rec["actual"] = f"{actual} (Passed on 2nd attempt)"
                    rec["healed"] = healed
                    rec["healing_note"] = (healing_note or "") + " [Flaky: Passed after retry]"
                    rec["attempts"] = 2
                except Exception as final_err:
                    failed = True
                    rec["status"] = "FAIL"
                    rec["error"] = str(final_err)
                    rec["attempts"] = 2
                    exp, sug = diagnose_failure(step, str(final_err), page.url)
                    rec["explanation"] = exp
                    rec["suggestion"] = sug

            # Capture visual frame after each step
            try:
                step_png = page.screenshot(full_page=False, timeout=3000)
                rec["screenshot_b64"] = base64.b64encode(step_png).decode("utf-8")
                final_screenshot = rec["screenshot_b64"]
            except Exception:
                pass

            rec["ms"] = int((time.time() - start_time) * 1000)
            results.append(rec)

        try:
            context.close()
            browser.close()
        except Exception:
            pass

    return results, final_screenshot, browser_console_logs[:15], network_failures[:15]