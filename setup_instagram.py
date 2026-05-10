#!/usr/bin/env python3
"""
인스타그램 & 쓰레드 API 설정 도우미
실행: python setup_instagram.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import webbrowser
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()
GRAPH = "https://graph.facebook.com/v19.0"


def step1_open_meta():
    console.print(Panel.fit(
        "[bold cyan]Step 1: Meta 개발자 앱 생성[/bold cyan]\n\n"
        "지금 브라우저가 열립니다.\n"
        "1. [green]'앱 만들기'[/green] 클릭\n"
        "2. 유형: [yellow]비즈니스[/yellow] 선택\n"
        "3. 앱 이름 입력 (예: my-sns-bot)\n"
        "4. 생성 완료 후 이 창으로 돌아오세요",
        border_style="cyan",
    ))
    input("\n준비되면 Enter를 누르세요...")
    webbrowser.open("https://developers.facebook.com/apps/")
    input("앱 생성 완료 후 Enter...")


def step2_open_explorer():
    console.print(Panel.fit(
        "[bold cyan]Step 2: Graph API Explorer에서 토큰 발급[/bold cyan]\n\n"
        "브라우저에서 아래 권한을 모두 체크하세요:\n"
        "  ✅ [green]instagram_basic[/green]\n"
        "  ✅ [green]instagram_content_publish[/green]\n"
        "  ✅ [green]pages_read_engagement[/green]\n"
        "  ✅ [green]pages_show_list[/green]\n"
        "  ✅ [green]threads_basic[/green] (쓰레드용)\n"
        "  ✅ [green]threads_content_publish[/green] (쓰레드용)\n\n"
        "권한 체크 후 [yellow]'토큰 생성'[/yellow] 클릭",
        border_style="cyan",
    ))
    input("\n준비되면 Enter를 누르세요...")
    webbrowser.open("https://developers.facebook.com/tools/explorer/")
    return Prompt.ask("\n생성된 [bold green]Access Token[/bold green]을 붙여넣으세요")


def step3_find_instagram_id(token: str) -> tuple[str, str]:
    """연결된 Instagram 계정 ID 자동 탐색"""
    console.print("\n[yellow]연결된 Instagram 계정 탐색 중...[/yellow]")

    # Facebook 페이지 목록 조회
    resp = requests.get(f"{GRAPH}/me/accounts", params={"access_token": token})
    if resp.status_code != 200:
        console.print(f"[red]오류: {resp.json().get('error', {}).get('message', '알 수 없음')}[/red]")
        console.print("[dim]Facebook 페이지와 Instagram이 연결되어 있는지 확인하세요.[/dim]")
        return "", ""

    pages = resp.json().get("data", [])
    if not pages:
        console.print("[red]연결된 Facebook 페이지가 없습니다.[/red]")
        console.print("Instagram 비즈니스 계정은 Facebook 페이지와 연결되어야 합니다.")
        return "", ""

    table = Table(title="연결된 Facebook 페이지")
    table.add_column("번호", width=5)
    table.add_column("페이지명")
    table.add_column("페이지 ID")

    for idx, page in enumerate(pages, 1):
        table.add_row(str(idx), page["name"], page["id"])
    console.print(table)

    page_idx = int(Prompt.ask("Instagram이 연결된 페이지 번호 선택", default="1")) - 1
    page = pages[page_idx]
    page_token = page["access_token"]
    page_id = page["id"]

    # Instagram 계정 ID 조회
    resp = requests.get(
        f"{GRAPH}/{page_id}",
        params={"fields": "instagram_business_account", "access_token": page_token},
    )
    ig_data = resp.json().get("instagram_business_account", {})
    ig_id = ig_data.get("id", "")

    if not ig_id:
        console.print("[red]이 페이지에 연결된 Instagram 비즈니스 계정이 없습니다.[/red]")
        console.print("Instagram 앱 > 설정 > 계정 유형 > 비즈니스로 전환 후 페이지 연결")
        return "", ""

    # Instagram 계정 정보 조회
    resp = requests.get(
        f"{GRAPH}/{ig_id}",
        params={"fields": "username,name", "access_token": page_token},
    )
    ig_info = resp.json()
    console.print(f"\n[green]✓ Instagram 계정 발견: @{ig_info.get('username', '')}[/green]")

    return ig_id, page_token


def step4_find_threads_id(token: str) -> tuple[str, str]:
    """Threads 계정 ID 자동 탐색"""
    console.print("\n[yellow]Threads 계정 탐색 중...[/yellow]")

    resp = requests.get(
        "https://graph.threads.net/v1.0/me",
        params={"fields": "id,username", "access_token": token},
    )

    if resp.status_code != 200:
        console.print(f"[dim]Threads ID 자동 조회 실패: {resp.json().get('error', {}).get('message', '')}[/dim]")
        threads_id = Prompt.ask("Threads User ID를 직접 입력하세요 (모르면 Enter 건너뜀)", default="")
        return threads_id, token

    data = resp.json()
    threads_id = data.get("id", "")
    console.print(f"[green]✓ Threads 계정: @{data.get('username', '')} (ID: {threads_id})[/green]")
    return threads_id, token


def step5_save_config(ig_id: str, ig_token: str, threads_id: str, threads_token: str):
    """config.yaml 자동 업데이트"""
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if ig_id:
        cfg["instagram"]["access_token"] = ig_token
        cfg["instagram"]["instagram_account_id"] = ig_id

    if threads_id:
        cfg["threads"]["access_token"] = threads_token
        cfg["threads"]["threads_user_id"] = threads_id

    with open("config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)

    console.print("\n[green bold]config.yaml 업데이트 완료![/green bold]")


def main():
    console.print(Panel.fit(
        "[bold cyan]인스타그램 & 쓰레드 API 설정 도우미[/bold cyan]",
        border_style="cyan",
    ))

    step1_open_meta()
    token = step2_open_explorer()

    if not token or token.strip() == "":
        console.print("[red]토큰이 입력되지 않았습니다.[/red]")
        return

    token = token.strip()

    ig_id, ig_token = step3_find_instagram_id(token)
    threads_id, threads_token = step4_find_threads_id(token)
    step5_save_config(ig_id, ig_token, threads_id, threads_token)

    console.print("\n[bold cyan]설정 완료! 이제 업로드를 테스트해보세요:[/bold cyan]")
    console.print("[dim]python main.py upload posts/test_post.yaml -p instagram -p threads[/dim]")


if __name__ == "__main__":
    main()
