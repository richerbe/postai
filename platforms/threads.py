import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from .base import BasePlatform, PostContent, UploadResult


class ThreadsUploader(BasePlatform):
    """Selenium을 사용한 쓰레드 자동 업로드 (ID/PW 방식)"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.username = config.get("username", "")
        self.password = config.get("password", "")

    def _get_driver(self) -> webdriver.Chrome:
        opts = Options()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def _login(self, driver: webdriver.Chrome, wait: WebDriverWait):
        driver.get("https://www.threads.net/login")
        time.sleep(3)

        try:
            # 인스타그램으로 로그인 버튼
            ig_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(),'Instagram으로') or contains(text(),'Instagram')]")
            ))
            ig_btn.click()
            time.sleep(3)
        except Exception:
            pass

        # 아이디/비밀번호 입력
        try:
            id_field = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[name='username'], input[autocomplete='username']")
            ))
            id_field.clear()
            id_field.send_keys(self.username)
            time.sleep(0.5)

            pw_field = driver.find_element(
                By.CSS_SELECTOR, "input[name='password'], input[type='password']"
            )
            pw_field.clear()
            pw_field.send_keys(self.password)
            pw_field.send_keys(Keys.RETURN)
            time.sleep(4)
        except Exception as e:
            raise RuntimeError(f"로그인 입력 실패: {e}")

    def upload(self, content: PostContent) -> UploadResult:
        if not self.enabled:
            return UploadResult("threads", False, error="Threads 비활성화")
        if not self.username or not self.password:
            return UploadResult("threads", False, error="username/password 미설정")

        driver = None
        try:
            driver = self._get_driver()
            wait = WebDriverWait(driver, 20)

            self._login(driver, wait)

            # 새 쓰레드 작성 버튼
            try:
                compose_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@href,'/intent/post') or @aria-label='새 스레드' or @aria-label='New thread']")
                ))
                compose_btn.click()
            except Exception:
                driver.get("https://www.threads.net/intent/post")
            time.sleep(2)

            # 본문 입력
            text_area = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[contenteditable='true'], textarea[placeholder]")
            ))
            text_area.click()
            text_area.send_keys(content.caption)
            time.sleep(1)

            # 이미지 첨부 (있을 경우)
            for img_path in content.image_paths:
                if Path(img_path).exists():
                    try:
                        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                        if file_inputs:
                            file_inputs[0].send_keys(str(Path(img_path).absolute()))
                            time.sleep(2)
                    except Exception:
                        pass

            # 게시 버튼
            post_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='button'][contains(text(),'게시') or contains(text(),'Post')]"
                           " | //button[contains(text(),'게시') or contains(text(),'Post')]")
            ))
            post_btn.click()
            time.sleep(3)

            return UploadResult(
                "threads", True,
                url=f"https://www.threads.net/@{self.username}",
            )

        except Exception as e:
            return UploadResult("threads", False, error=str(e))
        finally:
            if driver:
                time.sleep(1)
                driver.quit()
