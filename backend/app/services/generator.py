TEMPLATES = {
    "navigate": 'page.goto("{value}")',
    "click": '{el}.click()',
    "dblclick": '{el}.dblclick()',
    "fill": '{el}.fill("{value}")',
    "clear": '{el}.clear()',
    "select": '{el}.select_option(label="{value}")',
    "hover": '{el}.hover()',
    "scroll": '{el}.scroll_into_view_if_needed()',
    "press": 'page.keyboard.press("{value}")',
    "assert_text_equals": 'assert {el}.inner_text().strip() == "{expected}"',
    "assert_text_contains": 'assert "{expected}" in {el}.inner_text()',
    "assert_visible": 'assert {el}.is_visible()',
    "assert_hidden": 'assert {el}.is_hidden()',
    "assert_url_equals": 'assert page.url == "{expected}"',
    "assert_title": 'assert page.title() == "{expected}"',
    "wait": 'page.wait_for_timeout({value})'
}

SELECTORS = {
    "css": 'page.locator("{s}")',
    "xpath": 'page.locator("xpath={s}")',
    "id": 'page.locator("#{s}")',
    "name": 'page.locator("[name=\'{s}\']")',
    "link": 'page.get_by_role("link", name="{s}")',
    "aria": 'page.get_by_label("{s}")'
}

def generate_script(case_data: dict, base_url: str = "") -> str:
    lines = [
        "from playwright.sync_api import sync_playwright",
        "",
        "def run_test():",
        "    with sync_playwright() as pw:",
        "        browser = pw.chromium.launch(headless=True)",
        "        page = browser.new_page()",
        f"        base_url = \"{base_url}\""
    ]
    
    for step in case_data.get("steps", []):
        action = step.get("action")
        sel_type = step.get("selector_type", "")
        sel_val = step.get("selector", "")
        val = step.get("value", "")
        expected = step.get("expected", "")

        el_code = ""
        if sel_type and sel_type in SELECTORS:
            el_code = SELECTORS[sel_type].format(s=sel_val)

        template = TEMPLATES.get(action, "# Unknown action: " + str(action))
        code = template.format(el=el_code, value=val, expected=expected)
        code = code.replace("{{BASE_URL}}", base_url)
        lines.append(f"        {code}")

    lines.append("        browser.close()")
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    run_test()")
    return "\n".join(lines)