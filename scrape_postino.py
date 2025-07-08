import asyncio
from playwright.sync_api import sync_playwright
from supabase import create_client
import time
import os

# --- Your Supabase credentials here ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- Step 1: Scrape the menu using Playwright ---
def scrape_menu(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        # Wait for menu to load
        page.wait_for_selector('[data-anchor-id="MenuItem"]', timeout=15000)

        menu_items = []

        sections = page.query_selector_all('[data-anchor-id="MenuItem"]')
        for section in sections:
            name_el = section.query_selector('[data-anchor-id="MenuItemTitle"]')
            desc_el = section.query_selector('[data-anchor-id="MenuItemDescription"]')
            price_el = section.query_selector('[data-anchor-id="MenuItemPrice"]')

            name = name_el.inner_text().strip() if name_el else "Unnamed Item"
            description = desc_el.inner_text().strip() if desc_el else ""
            price_str = price_el.inner_text().replace("$", "").strip() if price_el else None

            try:
                price = float(price_str) if price_str else None
            except:
                price = None

            menu_items.append({
                "name": name,
                "description": description,
                "price": price
            })

        browser.close()
        return menu_items

# --- Step 2: Insert into Supabase ---
def upsert_restaurant(name, city="Tempe", state="AZ", address=None):
    result = supabase.table("restaurants").select("id").eq("name", name).eq("city", city).execute()
    if result.data:
        return result.data[0]["id"]
    else:
        res = supabase.table("restaurants").insert({
            "name": name,
            "city": city,
            "state": state,
            "address": address
        }).execute()
        return res.data[0]["id"]

def upsert_menu_items(restaurant_id, items):
    for item in items:
        existing = supabase.table("menu_items").select("id").eq("restaurant_id", restaurant_id).eq("name", item["name"]).execute()
        if existing.data:
            print(f"Found existing item: {item['name']}")
            continue  # or update if needed
        else:
            print(f"Inserting new item: {item['name']}")
            supabase.table("menu_items").insert({
                "restaurant_id": restaurant_id,
                "name": item["name"],
                "description": item["description"],
                "price": item["price"],
                "status": "active"
            }).execute()
            time.sleep(0.2)  # optional rate limit

# --- Main ---
if __name__ == "__main__":
    url = "https://www.doordash.com/store/postino-tempe-12850/20170559/"
    print("Scraping Postino Tempe...")
    menu = scrape_menu(url)
    print(f"Found {len(menu)} items.")

    print("Upserting into Supabase...")
    restaurant_id = upsert_restaurant("Postino", city="Tempe", state="AZ")
    upsert_menu_items(restaurant_id, menu)
    print("Done.")
