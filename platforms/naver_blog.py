import json
import time
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from .base import BasePlatform, PostContent, UploadResult

COOKIE_FILE = Path("naver_cookies.json")


def _slow_type(element, text: str, delay: float = 0.04):
    for ch in text:
        element.send_keys(ch)
        time.sleep(delay + random.uniform(0, 0.03))


class NaverBlogUploader(BasePlatform):
    """네이버 블로그 스마트에디터3 자동 업로드"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.naver_id       = config.get("naver_id", "")
        self.naver_password = config.get("naver_password", "")
        self.blog_id        = config.get("blog_id", self.naver_id)

    def _get_driver(self) -> webdriver.Chrome:
        opts = Options()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--window-size=1280,900")
        opts.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service, options=opts)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"},
        )
        return driver

    # ── 쿠키 저장 / 불러오기 ─────────────────────────────
    def _save_cookies(self, driver: webdriver.Chrome):
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(driver.get_cookies(), f, ensure_ascii=False)

    def _load_cookies(self, driver: webdriver.Chrome) -> bool:
        if not COOKIE_FILE.exists():
            return False
        driver.get("https://www.naver.com")
        time.sleep(1)
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        for c in cookies:
            try:
                driver.add_cookie(c)
            except Exception:
                pass
        driver.refresh()
        time.sleep(2)
        # 로그인 확인: 내 아이디가 보이면 성공
        return self.naver_id.lower() in driver.page_source.lower()

    # ── 수동 로그인 (캡차용) ─────────────────────────────
    def manual_login(self):
        """최초 1회 수동 로그인 → 쿠키 저장. 앱 설정 메뉴에서 호출."""
        # 시크릿 모드 사용 — 기존 저장 계정 자동로그인 방지
        opts = Options()
        opts.add_argument("--incognito")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--window-size=1100,800")
        opts.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"},
        )
        try:
            driver.get("https://nid.naver.com/nidlogin.login?mode=form")
            print("브라우저에서 로그인 후 Enter를 누르세요...")

            # 아이디/비번 자동 입력 시도 (캡차 없으면 자동, 있으면 수동)
            try:
                wait = WebDriverWait(driver, 5)
                id_box = wait.until(EC.presence_of_element_located((By.ID, "id")))
                id_box.click()
                _slow_type(id_box, self.naver_id)
                pw_box = driver.find_element(By.ID, "pw")
                pw_box.click()
                _slow_type(pw_box, self.naver_password)
                driver.find_element(By.ID, "log.login").click()
                time.sleep(3)
            except Exception:
                pass

            # 로그인 완료될 때까지 대기 (최대 3분)
            for _ in range(36):
                if "nidlogin" not in driver.current_url and "captcha" not in driver.current_url:
                    break
                time.sleep(5)

            if "nidlogin" in driver.current_url or "captcha" in driver.current_url:
                raise RuntimeError("로그인 시간 초과")

            self._save_cookies(driver)
            return True
        finally:
            driver.quit()

    # ── 글쓰기 ───────────────────────────────────────────
    def _dismiss_alerts(self, driver: webdriver.Chrome, tries: int = 5):
        for _ in range(tries):
            try:
                driver.switch_to.alert.accept()
                time.sleep(0.3)
            except Exception:
                break

    def _enter_editor_frame(self, driver: webdriver.Chrome, wait: WebDriverWait):
        """SE3 에디터는 #mainFrame iframe 안에 있음"""
        driver.switch_to.default_content()
        frame = wait.until(EC.presence_of_element_located((By.ID, "mainFrame")))
        driver.switch_to.frame(frame)
        time.sleep(0.5)

    def _js_click(self, driver: webdriver.Chrome, element):
        """오버레이에 가려진 버튼도 클릭 가능한 JavaScript click"""
        driver.execute_script("arguments[0].click();", element)

    def _write_post(self, driver: webdriver.Chrome, wait: WebDriverWait, content: PostContent):
        driver.get("https://blog.naver.com/GoBlogWrite.naver")
        time.sleep(8)
        self._dismiss_alerts(driver)

        # SE3 iframe 진입 (에디터 완전 로딩 대기)
        self._enter_editor_frame(driver, wait)
        time.sleep(3)

        # ── 제목 ────────────────────────────────────────
        # SE3 제목 영역: contenteditable div
        try:
            title_el = driver.execute_script(
                "return document.querySelector('.se-title-input') "
                "|| document.querySelector('[contenteditable][class*=title]');"
            )
            if title_el:
                self._js_click(driver, title_el)
                time.sleep(0.4)
                title_el.send_keys(content.title)
                time.sleep(0.5)
        except Exception:
            pass

        # ── 본문 ────────────────────────────────────────
        # 에디터 영역 클릭 후 클립보드 붙여넣기
        try:
            body_el = driver.execute_script(
                "return document.querySelector('.se-main-container') "
                "|| document.querySelector('[class*=se-component-content]');"
            )
            if body_el:
                self._js_click(driver, body_el)
                time.sleep(0.5)
        except Exception:
            pass

        try:
            import pyperclip
            pyperclip.copy(content.caption)
            ActionChains(driver).key_down(Keys.COMMAND).send_keys("v").key_up(Keys.COMMAND).perform()
            time.sleep(1)
        except Exception:
            try:
                driver.switch_to.active_element.send_keys(content.caption)
            except Exception:
                pass

        # ── 이미지 ──────────────────────────────────────
        for img_path in content.image_paths:
            if not Path(img_path).exists():
                continue
            try:
                photo_btn = driver.execute_script(
                    "return Array.from(document.querySelectorAll('button'))"
                    ".find(b => b.textContent.includes('사진') || b.className.includes('image'));"
                )
                if photo_btn:
                    self._js_click(driver, photo_btn)
                    time.sleep(2)
                fi = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
                fi.send_keys(str(Path(img_path).absolute()))
                time.sleep(3)
            except Exception:
                pass

        # ── 태그 ────────────────────────────────────────
        try:
            tag_in = driver.execute_script(
                "return document.querySelector('input[placeholder*=\"태그\"]') "
                "|| document.querySelector('[class*=tag_input] input') "
                "|| document.querySelector('#tagInput');"
            )
            if tag_in:
                for tag in content.hashtags[:10]:
                    clean = tag.lstrip("#")
                    self._js_click(driver, tag_in)
                    _slow_type(tag_in, clean, delay=0.03)
                    time.sleep(0.3)
                    tag_in.send_keys(Keys.RETURN)
                    time.sleep(0.3)
        except Exception:
            pass

    def _publish(self, driver: webdriver.Chrome, wait: WebDriverWait):
        # 발행 버튼: JavaScript click으로 오버레이 무시
        publish_btn = driver.execute_script(
            "return Array.from(document.querySelectorAll('button'))"
            ".find(b => b.className.includes('publish_btn') || b.textContent.trim() === '발행');"
        )
        if not publish_btn:
            raise RuntimeError("발행 버튼을 찾지 못했습니다.")

        self._js_click(driver, publish_btn)
        time.sleep(3)

        # 발행 확인 팝업
        for txt in ["발행", "확인", "공개"]:
            try:
                ok_btn = driver.execute_script(
                    f"return Array.from(document.querySelectorAll('button'))"
                    f".find(b => b.textContent.includes('{txt}'));"
                )
                if ok_btn:
                    self._js_click(driver, ok_btn)
                    time.sleep(2)
                    break
            except Exception:
                continue

    def upload(self, content: PostContent) -> UploadResult:
        if not self.enabled:
            return UploadResult("naver_blog", False, error="네이버 블로그 비활성화")
        if not self.naver_id or not self.naver_password:
            return UploadResult("naver_blog", False, error="네이버 아이디/비밀번호 미설정")

        driver = None
        try:
            driver = self._get_driver()
            wait   = WebDriverWait(driver, 25)

            # 저장된 쿠키로 로그인 시도 → 실패 시 수동 로그인
            if not self._load_cookies(driver):
                ok = self.manual_login()
                if not ok:
                    return UploadResult("naver_blog", False, error="로그인 실패")
                # 새 드라이버로 쿠키 재적용
                driver.quit()
                driver = self._get_driver()
                wait   = WebDriverWait(driver, 25)
                if not self._load_cookies(driver):
                    return UploadResult("naver_blog", False, error="쿠키 적용 실패")

            self._write_post(driver, wait, content)
            # _write_post 후 iframe 컨텍스트 확인 및 재진입
            self._enter_editor_frame(driver, wait)
            self._publish(driver, wait)

            return UploadResult(
                "naver_blog", True,
                url=f"https://blog.naver.com/{self.blog_id}",
            )
        except Exception as e:
            return UploadResult("naver_blog", False, error=str(e))
        finally:
            if driver:
                time.sleep(2)
                driver.quit()
