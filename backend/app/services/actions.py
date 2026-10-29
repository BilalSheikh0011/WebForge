def resolve(text: str, row: dict = None) -> str:
    if not text:
        return ""
    for key, val in (row or {}).items():
        text = text.replace("{{" + key + "}}", str(val))
    return text

def locate(page, step: dict):
    kind = step.get("selector_type")
    sel = step.get("selector", "")
    if kind == "css":   return page.locator(sel)
    if kind == "xpath": return page.locator("xpath=" + sel)
    if kind == "id":    return page.locator("#" + sel)
    if kind == "name":  return page.locator(f"[name='{sel}']")
    if kind == "link":  return page.get_by_role("link", name=sel)
    if kind == "aria":  return page.get_by_label(sel)
    raise ValueError(f"Unknown selector type: {kind}")

def check(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected '{expected}', got '{actual}'")
    return actual

ACTIONS = {
    "navigate": lambda pg, s, r: (pg.goto(resolve(s.get("value", ""), r)), pg.url)[1],
    "click": lambda pg, s, r: (locate(pg, s).click(), "clicked")[1],
    "fill": lambda pg, s, r: (locate(pg, s).fill(resolve(s.get("value", ""), r)), "filled")[1],
    "assert_text_equals": lambda pg, s, r: check(locate(pg, s).inner_text().strip(), resolve(s.get("expected", ""), r), "Text"),
    "assert_url_equals": lambda pg, s, r: check(pg.url, resolve(s.get("expected", ""), r), "URL"),
    "wait": lambda pg, s, r: (pg.wait_for_timeout(int(s.get("value") or 1000)), "waited")[1]
}