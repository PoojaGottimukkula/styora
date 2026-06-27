from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json


def get_high_res_image_url(element):
    """Extract the best available Amazon image URL for a Selenium image element."""
    if element is None:
        return None

    # Prefer any explicit high-resolution attributes if provided.
    hires = element.get_attribute("data-old-hires")
    if hires:
        hires = hires.strip()
        if hires.startswith("//"):
            hires = "https:" + hires
        if hires.startswith("http"):
            return hires

    dynamic_json = element.get_attribute("data-a-dynamic-image")
    if dynamic_json:
        try:
            dynamic_data = json.loads(dynamic_json)
            if isinstance(dynamic_data, dict) and dynamic_data:
                best_url = max(dynamic_data.keys(), key=lambda k: dynamic_data[k][0] * dynamic_data[k][1])
                if best_url.startswith("//"):
                    best_url = "https:" + best_url
                return best_url
        except Exception:
            pass

    src = element.get_attribute("src")
    if not src:
        return None

    src = src.strip()
    if src.startswith("//"):
        src = "https:" + src

    # Normalize common Amazon size tokens to a larger resolution.
    high_res = re.sub(
        r'(_SX\d+_|_SS\d+_|_SY\d+_|_SL\d+_|_UX\d+_|_US\d+_)',
        '_SL1500_',
        src,
    )
    return high_res or src


def get_product_images(driver):
    images = []

    try:
        # Get main image
        main_img = driver.find_element(By.ID, "landingImage")
        main_src = get_high_res_image_url(main_img)
        if main_src:
            images.append(main_src)

        # Get additional images from gallery
        elements = driver.find_elements(By.CSS_SELECTOR, "#altImages img")
        for e in elements:
            src = get_high_res_image_url(e)
            if src:
                images.append(src)

    except Exception as e:
        print(f"Error getting images: {e}")

    return list(dict.fromkeys(images))  # Preserve order and remove duplicates
def get_product_details(driver):

    data = {
        "title": None,
        "price": None,
        "rating": None,
        "reviews": None,
        "description": None,
        "images": []
    }

    try:
        WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.ID,"productTitle"))
        )
    except:
        pass

    driver.execute_script("window.scrollTo(0,800)")

    # TITLE
    try:
        data["title"] = driver.find_element(By.ID,"productTitle").text.strip()
    except:
        pass

    # PRICE
    price_selectors = [
        ".a-price .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#corePrice_feature_div .a-offscreen",
        "#price_inside_buybox"
    ]

    for selector in price_selectors:
        try:
            price = driver.find_element(By.CSS_SELECTOR,selector).text
            if price:
                data["price"] = price
                break
        except:
            continue

    # RATING
    try:
        data["rating"] = driver.find_element(
            By.CSS_SELECTOR,"span[data-hook='rating-out-of-text']"
        ).text
    except:
        pass

    # REVIEWS
    try:
        data["reviews"] = driver.find_element(
            By.ID,"acrCustomerReviewText"
        ).text
    except:
        pass

    # IMAGE
    try:
        # data["image"] = driver.find_element(
        #     By.ID,"landingImage"
        # ).get_attribute("src")
        data["images"] = get_product_images(driver)
    except:
        pass

    # DESCRIPTION
    try:
        bullets = driver.find_elements(By.CSS_SELECTOR,"#feature-bullets li span")

        desc = []

        for b in bullets:
            text = b.text.strip()
            if text:
                desc.append(text)

        if desc:
            data["description"] = " ".join(desc)

    except:
        pass

    return data