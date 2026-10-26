"""Scan, on a POS limited to some categories, of a product outside them.

Usage: python3 parcours.py <port> <db> <out.png>
"""

import sys

from playwright.sync_api import sync_playwright

PORT, DB, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
CONFIG_ID = 3  # "Boulangerie": limited to Pains / Pâtisseries
BARCODE = "6016478556493"  # "Poubelle à pédale", category Divers
URL = f"http://{DB}:{PORT}"
SVC = "odoo.__WOWL_DEBUG__.root.env.services"

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True, args=[f"--host-resolver-rules=MAP {DB} 127.0.0.1"]
    )
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto(f"{URL}/web/login?db={DB}")
    page.fill('input[name="login"]', "admin")
    page.fill('input[name="password"]', "admin")
    page.click('.oe_login_form button[type="submit"]')
    page.wait_for_selector(".o_main_navbar", timeout=60000)

    page.goto(f"{URL}/pos/ui?config_id={CONFIG_ID}")
    # Opening control, then the product screen, with no modal on top.
    for _ in range(60):
        page.wait_for_timeout(1000)
        opening = page.get_by_text("Ouvrir la caisse", exact=True)
        if opening.count() and opening.last.is_visible():
            opening.last.click(force=True)
            continue
        if (
            page.locator(".product-list").count()
            and not page.locator(".modal.d-block").count()
        ):
            break
    else:
        raise SystemExit("product screen never shown")

    loaded = page.evaluate(
        f"(b) => !!{SVC}.pos.models['product.product'].getBy('barcode', b)", BARCODE
    )
    assert not loaded, "product already loaded: the scan would not reach the server"

    # Start from an empty order, whatever the session restored.
    page.evaluate(f"() => {SVC}.pos.add_new_order()")
    page.wait_for_timeout(1000)
    page.evaluate(
        f"(b) => {SVC}.barcode.bus.trigger('barcode_scanned', {{barcode: b}})", BARCODE
    )
    page.wait_for_timeout(4000)

    lines = page.evaluate(
        f"() => {SVC}.pos.get_order().lines.map(l => l.product_id.display_name)"
    )
    dialog = page.locator(".modal.d-block, .o_notification").all_inner_texts()
    sys.stdout.write(f"lines: {lines}\ndialog: {dialog}\n")
    page.screenshot(path=OUT)
    browser.close()
