from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os


def get_goldbox_products(driver=None, limit=50):
    """Return up to `limit` Amazon Goldbox product URLs.

    If `driver` is not provided, this helper will create its own headless driver.
    """

    owns_driver = False
    if driver is None:
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(options=opts)
        owns_driver = True

    # File to store links
    links_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "product_links.txt")

    # Load existing links
    product_links = set()
    if os.path.exists(links_file):
        with open(links_file, "r") as f:
            for line in f:
                product_links.add(line.strip())

    urls = [
        "https://www.amazon.in/gp/goldbox",
        "https://www.amazon.in/deals",
        "https://www.amazon.in/gp/movers-and-shakers",
        "https://www.amazon.in/gp/bestsellers/electronics",
        "https://www.amazon.in/gp/bestsellers/kitchen",
        "https://www.amazon.in/gp/bestsellers/fashion",
        "https://www.amazon.in/gp/bestsellers/books",
        "https://www.amazon.in/gp/bestsellers/home-improvement"
    ]

    new_links = set()

    for url in urls:
        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/dp/']"))
            )
        except:
            pass

        previous_count = len(new_links)

        # Scroll a few times to load more products, but avoid long sleeps.
        for _ in range(8):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            products = driver.find_elements(By.CSS_SELECTOR, "a[href*='/dp/']")

            for p in products:
                link = p.get_attribute("href")
                if link and "/dp/" in link:
                    clean_link = link.split("?")[0]
                    if clean_link not in product_links:
                        new_links.add(clean_link)

                    if len(product_links) + len(new_links) >= limit:
                        break

            if len(product_links) + len(new_links) >= limit:
                break

            if len(new_links) == previous_count:
                break

            previous_count = len(new_links)

        if len(product_links) + len(new_links) >= limit:
            break

    # Combine and save
    all_links = product_links.union(new_links)

    with open(links_file, "w") as f:
        for link in all_links:
            f.write(link + "\n")

    if owns_driver:
        driver.quit()

    # Return up to limit
    return list(all_links)[:limit]
