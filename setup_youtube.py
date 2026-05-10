#!/usr/bin/env python3
"""
YouTube API 설정 도우미
실행: python setup_youtube.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import webbrowser
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


def main():
    console.print(Panel.fit(
        "[bold red]YouTube Data API v3 설정 도우미[/bold red]",
        border_style="red",
    ))

    # Step 1
    console.print(Panel(
        "[bold]Step 1: Google Cloud 프로젝트 생성[/bold]\n\n"
        "1. 브라우저에서 Google Cloud Console이 열립니다\n"
        "2. [yellow]'새 프로젝트'[/yellow] 만들기 (이름: sns-automation)\n"
        "3. 프로젝트 선택 후 다음으로",
        border_style="dim",
    ))
    input("Enter를 누르면 브라우저가 열립니다...")
    webbrowser.open("https://console.cloud.google.com/projectcreate")
    input("프로젝트 생성 완료 후 Enter...")

    # Step 2
    console.print(Panel(
        "[bold]Step 2: YouTube Data API v3 활성화[/bold]\n\n"
        "1. 검색창에 'YouTube Data API v3' 검색\n"
        "2. [yellow]'사용 설정'[/yellow] 클릭",
        border_style="dim",
    ))
    input("Enter를 누르면 API 라이브러리가 열립니다...")
    webbrowser.open("https://console.cloud.google.com/apis/library/youtube.googleapis.com")
    input("API 활성화 완료 후 Enter...")

    # Step 3
    console.print(Panel(
        "[bold]Step 3: OAuth 동의 화면 설정[/bold]\n\n"
        "1. 사용자 유형: [yellow]외부[/yellow] 선택\n"
        "2. 앱 이름 입력 (예: SNS 자동화)\n"
        "3. 이메일 입력 후 저장\n"
        "4. 테스트 사용자에 본인 구글 계정 추가",
        border_style="dim",
    ))
    input("Enter를 누르면 동의 화면 설정이 열립니다...")
    webbrowser.open("https://console.cloud.google.com/apis/credentials/consent")
    input("동의 화면 설정 완료 후 Enter...")

    # Step 4
    console.print(Panel(
        "[bold]Step 4: OAuth 2.0 클라이언트 ID 생성[/bold]\n\n"
        "1. [yellow]'+ 사용자 인증 정보 만들기'[/yellow] 클릭\n"
        "2. 'OAuth 클라이언트 ID' 선택\n"
        "3. 애플리케이션 유형: [yellow]데스크톱 앱[/yellow] 선택\n"
        "4. 이름 입력 후 만들기\n"
        "5. [green]'JSON 다운로드'[/green] 클릭",
        border_style="dim",
    ))
    input("Enter를 누르면 사용자 인증 정보 페이지가 열립니다...")
    webbrowser.open("https://console.cloud.google.com/apis/credentials")
    input("JSON 다운로드 완료 후 Enter...")

    # Step 5: 파일 이동
    console.print("\n[yellow]다운로드된 JSON 파일 경로를 입력하세요:[/yellow]")
    console.print("[dim](예: /Users/macbook/Downloads/client_secret_xxx.json)[/dim]")

    json_path = Prompt.ask("JSON 파일 경로").strip().strip('"').strip("'")

    if json_path and Path(json_path).exists():
        import shutil
        dest = Path(__file__).parent / "youtube_client_secrets.json"
        shutil.copy(json_path, dest)
        console.print(f"[green]✓ youtube_client_secrets.json 복사 완료![/green]")
    else:
        console.print(f"[red]파일을 찾을 수 없습니다. 수동으로 복사하세요:[/red]")
        console.print(f"[dim]파일명을 'youtube_client_secrets.json'으로 바꿔서 자동화 폴더에 넣어주세요[/dim]")
        return

    # Step 6: 인증 테스트
    console.print(Panel(
        "[bold]Step 5: YouTube 인증 테스트[/bold]\n\n"
        "브라우저에서 구글 로그인 화면이 열립니다.\n"
        "로그인 후 '허용'을 클릭하면 인증이 완료됩니다.\n\n"
        "[dim](최초 1회만 필요. 이후 자동 로그인됩니다.)[/dim]",
        border_style="dim",
    ))
    input("Enter를 누르면 인증을 시작합니다...")

    try:
        from platforms.youtube import YouTubeUploader
        import yaml

        with open("config.yaml", "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        uploader = YouTubeUploader(cfg["youtube"])
        uploader._authenticate()
        console.print("[green bold]✓ YouTube 인증 완료! youtube_token.pickle 저장됨[/green bold]")

    except Exception as e:
        console.print(f"[red]인증 오류: {e}[/red]")
        return

    console.print("\n[bold cyan]YouTube 설정 완료![/bold cyan]")
    console.print("[dim]이제 동영상을 업로드할 수 있습니다:[/dim]")
    console.print("[dim]python main.py upload posts/my_video.yaml -p youtube[/dim]")


if __name__ == "__main__":
    main()
