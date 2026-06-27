import sys
import time
import json
import re
import os
import threading

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), ".env"))
except ImportError:
    pass

try:
    from selenium import webdriver
    from selenium.common.exceptions import SessionNotCreatedException
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please run using the project virtual environment:")
    print("  /Users/pooja/Documents/styora/venv/bin/python /Users/pooja/Documents/styora/main.py")
    print("Or install Selenium in your active Python environment:")
    print("  pip install selenium")
    sys.exit(1)

from scraper.amazon_scraper import get_goldbox_products
from scraper.product_details import get_product_details
from utils.affiliate import generate_affiliate_link, shorten_link, expand_short
from utils.caption_generator import generate_caption
from utils.email_utils import send_preview_email, check_approval_emails
from utils.image_utils import download_image
from utils.instagram_poster import post_to_instagram


# rest of your code
def main():

    # options = Options()
    # # options.add_argument("--start-maximized")

    def create_browser_driver():
        """Create a Selenium browser driver.
        
        Tries Chrome with Chromedriver first, falls back to Safari.
        """
        opts = webdriver.ChromeOptions()
        profile_dir = os.path.join(os.getcwd(), "chrome_profile")
        opts.add_argument(f"--user-data-dir={profile_dir}")
        opts.add_argument("--profile-directory=Default")
        opts.add_argument("--remote-allow-origins=*")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        # Try Chrome with chromedriver (Selenium will auto-detect chromedriver)
        try:
            print("Attempting to start Chrome with Chromedriver...")
            return webdriver.Chrome(options=opts)
        except Exception as chrome_exc:
            print(f"Chrome failed: {chrome_exc}")
            print("Attempting Safari WebDriver fallback...")
            try:
                return webdriver.Safari()
            except Exception as safari_exc:
                print(f"Safari failed: {safari_exc}")
                raise RuntimeError("No compatible browser driver available. Install Google Chrome or enable Safari remote automation.")

    try:
        driver = create_browser_driver()
    except Exception as e:
        print("Failed to launch browser:", e)
        print("Please ensure a supported browser is installed and Selenium WebDriver is configured correctly.")
        raise

    print("Fetching deals...")

    products = get_goldbox_products(driver, limit=20)

    print(f"Found {len(products)} products")

    stop_event = threading.Event()
    driver_lock = threading.Lock()
    os.makedirs("approvals", exist_ok=True)

    def approval_monitor():
        print("Approval monitor started.")
        while not stop_event.is_set():
            approvals = check_approval_emails()
            if approvals:
                print(f"Found approvals for products: {approvals}")
                for product_id in approvals:
                    for file in os.listdir('approvals'):
                        if file.startswith('approval_') and file.endswith('.json') and not file.endswith('_posted.json'):
                            with open(os.path.join('approvals', file), 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if data.get('product_id') == product_id:
                                    image_path = data.get('image_path')
                                    caption_text = data.get('caption')
                                    if not image_path or not caption_text:
                                        print(f"Skipping approval file {file}: missing image_path or caption")
                                        continue
                                    print(f"Posting approved product {product_id}")
                                    with driver_lock:
                                        posted = post_to_instagram(driver, [image_path], caption_text)
                                    if posted:
                                        os.rename(
                                            os.path.join('approvals', file),
                                            os.path.join('approvals', file.replace('.json', '_posted.json'))
                                        )
                                    else:
                                        print(f"Post failed for {product_id}; approval file retained for retry")
                                    break
            stop_event.wait(10)
        print("Approval monitor stopped.")

    monitor_thread = threading.Thread(target=approval_monitor, daemon=True)
    monitor_thread.start()

    for url in products:

        try:

            print("\nOpening:", url)

            original_url = url
            if not re.search(r'/dp/([A-Z0-9]+)', original_url):
                original_url = expand_short(url)

            match = re.search(r'/dp/([A-Z0-9]+)', original_url)
            if match:
                product_id = match.group(1)
                original_url = f"https://www.amazon.in/dp/{product_id}"
            else:
                original_url = original_url.split('?')[0]

            with driver_lock:
                driver.get(original_url)

                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#landingImage, #productTitle"))
                    )
                except:
                    pass

                details = get_product_details(driver)

            affiliate_url = generate_affiliate_link(original_url)
            short = shorten_link(affiliate_url)

            caption = generate_caption(details, short)

            print("\nGenerated Post:\n")
            print(caption)

            # confirm = input("\nPost this? (y/n): ")

            # if confirm.lower() == "y":

            #     # image_path = "product.jpg"   # we will generate this next
            #     images = details.get("images", [])
            #     paths = download_multiple_images(images)
            #     paths = paths[:10]

            #     post_to_instagram(paths, caption)

            # else:
            #     print("Skipped")
            images = details.get("images", [])
            if not images:
                print("No images found")
                continue

            chosen_url = images[0]

            # Download the chosen high-res image
            filename = f"images/product_{products.index(url)}.jpg"
            path = download_image(chosen_url, filename)
            print(f"Downloaded high-res image: {path}")

            output = {
                "image_path": filename,
                "caption": caption,
                "link": short,
                "product_id": product_id
            }

            print(json.dumps(output))

            # Save approval data for later posting
            os.makedirs("approvals", exist_ok=True)
            approval_file = os.path.join("approvals", f"approval_{product_id}.json")
            with open(approval_file, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
            print(f"Saved approval data to {approval_file}")

            preview_email = os.getenv("PREVIEW_EMAIL")
            if not preview_email:
                print("PREVIEW_EMAIL is not configured; skipping preview email.")
                continue

            subject = f"Instagram Post Preview: {details.get('title', 'Product Deal')}"
            body = (
                f"Product: {details.get('title', 'Unknown')}\n"
                f"Deal price: {details.get('price', 'N/A')}\n"
                f"Link: {short}\n\n"
                f"Caption:\n{caption}\n"
            )

            email_sent = send_preview_email(
                preview_email,
                subject,
                body,
                attachment_path=filename,
                approval_links=True,
                product_id=product_id,
            )
            if email_sent:
                print(f"Preview email sent to {preview_email}.")
            else:
                print("Could not send preview email. Check email configuration and try again.")

        except Exception as e:
            print("Error:", e)

    print("All preview emails sent. Still monitoring approvals... (Press Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping approval monitor...")
        stop_event.set()
        monitor_thread.join()

    driver.quit()


if __name__ == "__main__":
    main()
