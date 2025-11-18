from playwright.sync_api import sync_playwright
import time

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto("http://127.0.0.1:5000")

            # Fill out the form
            page.fill("#email", "test@example.com")
            page.fill("#secret", "test-secret")
            page.fill("#task", "Test Task")
            page.fill("#brief", "Test Brief")

            # Submit the form
            page.click("#submitBtn")

            # Wait for the error message to appear
            page.wait_for_selector("h3:has-text('❌ Error')", timeout=30000)
            print("Test passed: Error message appeared as expected.")

        except Exception as e:
            print(f"Test failed: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run_test()
