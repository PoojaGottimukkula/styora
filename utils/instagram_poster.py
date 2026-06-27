from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os


def filter_bmp(text):
    """Filter text to only include BMP characters to avoid ChromeDriver issues."""
    return ''.join(c for c in text if ord(c) <= 0xFFFF)


def post_to_instagram(driver, image_paths, caption):

    wait = WebDriverWait(driver, 20)

    print("Opening Instagram...")
    driver.get("https://www.instagram.com")
    
    # Check if logged in
    time.sleep(3)
    current_url = driver.current_url
    if "login" in current_url.lower() or "accounts/login" in current_url:
        print("Not logged in to Instagram. Please log in manually in the Chrome profile and try again.")
        return False
    
    try:
        login_elements = driver.find_elements(By.XPATH, "//input[@name='username'] | //input[@name='password'] | //button[contains(text(), 'Log in')]")
        if login_elements:
            print("Login form detected. Not logged in.")
            return False
    except:
        pass
    
    print("Appears logged in, proceeding to create post.")

    driver.get("https://www.instagram.com/create/select/")

    try:
        file_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        driver.execute_script("arguments[0].style.display = 'block';", file_input)

        print("Uploading image...")
        file_input.send_keys(os.path.abspath(image_paths[0]))

    except Exception as e:
        print("Could not upload image.")
        print(e)
        return False

    # Wait for the first Next button after upload
    try:
        next_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(translate(normalize-space(.), 'NEXT', 'next'), 'next') or contains(@aria-label, 'Next') or contains(@title, 'Next')]"
                )
            )
        )
        next_btn.click()

    except Exception as e:
        print("Next button not found (step 1)")
        print(e)
        return False

    time.sleep(3)

    # Second Next button
    try:
        next_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(translate(normalize-space(.), 'NEXT', 'next'), 'next') or contains(@aria-label, 'Next') or contains(@title, 'Next')]"
                )
            )
        )
        next_btn.click()

    except Exception as e:
        print("Next button not found (step 2)")
        print(e)
        return False

    time.sleep(3)

    # CAPTION
    try:
        caption_box = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//textarea[contains(@aria-label, 'caption') or contains(@placeholder, 'caption')] | //div[@role='textbox']"
                )
            )
        )

        caption_box.click()
        # Filter caption to BMP only
        safe_caption = filter_bmp(caption)
        if caption_box.tag_name.lower() == 'textarea':
            caption_box.clear()
            caption_box.send_keys(safe_caption)
        else:
            # For div textbox
            caption_box.clear()
            caption_box.send_keys(safe_caption)

        print("Caption added")

    except Exception as e:
        print("Caption box not found")
        print(e)
        return False

    print("\nPreview ready on Instagram")

    # SHARE
    try:
        print("Looking for share button...")
        share_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(translate(normalize-space(.), 'SHARE', 'share'), 'share') or contains(@aria-label, 'Share') or contains(@title, 'Share') or contains(text(), 'Share') or contains(text(), 'Post')]"
                )
            )
        )
        print("Share button found, clicking...")
        share_btn.click()
        print("Share button clicked")

        # Wait for posting confirmation
        time.sleep(5)
        
        # Check for errors
        try:
            error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'error') or contains(text(), 'Error') or contains(text(), 'failed') or contains(text(), 'Failed')]")
            if error_elements:
                print("Possible error found:", [e.text for e in error_elements])
                return False
        except:
            pass
        
        # Check if still on create page or redirected
        current_url = driver.current_url
        if "create" in current_url:
            print("Still on create page, post may not have been submitted")
            return False
        
        print("Post uploaded successfully!")
        return True

    except Exception as e:
        print("Share button not found")
        print(e)
        return False