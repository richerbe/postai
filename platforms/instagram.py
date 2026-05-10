import time
from pathlib import Path
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from .base import BasePlatform, PostContent, UploadResult


class InstagramUploader(BasePlatform):
    """Selenium 모바일 에뮬레이션으로 인스타그램 업로드"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.username = config.get("username", "")
        self.password = config.get("password", "")

    def _get_driver(self) -> webdriver.Chrome:
        opts = Options()

        # iPhone 모바일 에뮬레이션 (업로드 버튼 활성화)
        mobile_emulation = {
            "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
            "userAgent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/17.0 Mobile/15E148 Safari/604.1"
            ),
        }
        opts.add_experimental_option("mobileEmulation", mobile_emulation)
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        return driver

    def _prepare_image(self, path: str) -> Path:
        """1080×1080 JPEG로 변환"""
        p = Path(path)
        out = p.parent / f"_ig_{p.stem}.jpg"
        img = Image.open(p).convert("RGB")
        img = img.resize((1080, 1080), Image.LANCZOS)
        img.save(out, "JPEG", quality=90)
        return out

    def _login(self, driver: webdriver.Chrome, wait: WebDriverWait):
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(3)

        # 쿠키 팝업 닫기
        try:
            cookie_btn = driver.find_element(By.XPATH, "//*[contains(text(),'허용') or contains(text(),'Allow')]")
            cookie_btn.click()
            time.sleep(1)
        except Exception:
            pass

        username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_input.clear()
        username_input.send_keys(self.username)
        time.sleep(0.5)

        password_input = driver.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys(self.password)
        time.sleep(0.5)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

        # "나중에 하기" 팝업 처리
        for _ in range(3):
            try:
                later_btn = driver.find_element(
                    By.XPATH,
                    "//*[contains(text(),'나중에') or contains(text(),'Not Now') or contains(text(),'나중에 하기')]"
                )
                later_btn.click()
                time.sleep(2)
            except Exception:
                break

    def _click_new_post(self, driver: webdriver.Chrome, wait: WebDriverWait):
        """새 게시물 버튼 클릭"""
        # 모바일 뷰의 하단 + 버튼
        for selector in [
            "svg[aria-label='새로운 게시물']",
            "svg[aria-label='New post']",
            "*[aria-label='새로운 게시물']",
            "*[aria-label='New post']",
        ]:
            try:
                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                btn.click()
                return
            except Exception:
                continue

        # XPath fallback
        btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[@aria-label='새로운 게시물' or @aria-label='New post']")
        ))
        btn.click()

    def upload(self, content: PostContent) -> UploadResult:
        if not self.enabled:
            return UploadResult("instagram", False, error="Instagram 비활성화")
        if not self.username or not self.password:
            return UploadResult("instagram", False, error="username/password 미설정")

        images = [p for p in content.image_paths if Path(p).exists()]
        if not images and not (content.video_path and Path(content.video_path or "").exists()):
            return UploadResult("instagram", False, error="이미지/영상 파일 없음")

        driver = None
        try:
            driver = self._get_driver()
            wait = WebDriverWait(driver, 25)

            self._login(driver, wait)
            time.sleep(2)

            # 새 게시물 클릭
            self._click_new_post(driver, wait)
            time.sleep(2)

            # 파일 선택 input에 이미지 경로 전달
            file_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='file']")
            ))

            if content.video_path and Path(content.video_path).exists():
                file_input.send_keys(str(Path(content.video_path).absolute()))
            else:
                prepared = self._prepare_image(images[0])
                file_input.send_keys(str(prepared.absolute()))
            time.sleep(4)

            # 다음 버튼 (여러 번 클릭 필요할 수 있음)
            for _ in range(3):
                try:
                    next_btn = driver.find_element(
                        By.XPATH,
                        "//button[contains(text(),'다음') or contains(text(),'Next')]"
                    )
                    next_btn.click()
                    time.sleep(2)
                except Exception:
                    break

            # 캡션 입력
            try:
                caption_area = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[aria-label='문구를 입력하세요...'], [aria-label='Write a caption...'], [contenteditable='true']")
                ))
                caption_area.click()
                caption_area.send_keys(content.caption)
                time.sleep(1)
            except Exception:
                pass

            # 공유 버튼
            share_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'공유') or contains(text(),'Share')]")
            ))
            share_btn.click()
            time.sleep(5)

            return UploadResult(
                "instagram", True,
                url=f"https://www.instagram.com/{self.username}/",
            )

        except Exception as e:
            return UploadResult("instagram", False, error=str(e))
        finally:
            if driver:
                time.sleep(2)
                driver.quit()
