#!/usr/bin/env python3
"""소셜미디어 멀티플랫폼 자동 업로드 시스템"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import click
from rich.console import Console

from platforms import (
    InstagramUploader, ThreadsUploader, YouTubeUploader,
    NaverBlogUploader, WordPressUploader,
)
from platforms.ai_content_generator import AIContentGenerator
from platforms.image_generator import AIImageGenerator
from content.manager import ContentManager
from scheduler.scheduler import PostScheduler
from utils.helpers import load_config, print_results

console = Console()

PLATFORM_MAP = {
    "instagram": (InstagramUploader, "instagram"),
    "threads":   (ThreadsUploader,   "threads"),
    "youtube":   (YouTubeUploader,   "youtube"),
    "naver":     (NaverBlogUploader, "naver_blog"),
    "wordpress": (WordPressUploader, "wordpress"),
}

PLATFORM_LABELS = {
    "instagram": "Instagram",
    "threads":   "Threads",
    "youtube":   "YouTube",
    "naver":     "네이버 블로그",
    "wordpress": "WordPress",
}


# ── 출력 헬퍼 ─────────────────────────────────────────────

def _header():
    console.print()
    console.print("[bold]소셜미디어 자동 업로드 시스템[/bold]")
    console.print("[dim]Instagram · Threads · YouTube · 네이버 블로그 · WordPress[/dim]")
    console.rule(style="dim")
    console.print()

def _ok(msg: str):
    console.print(f"  [green]✓[/green]  {msg}")

def _info(msg: str):
    console.print(f"  [dim]{msg}[/dim]")

def _err(msg: str):
    console.print(f"\n  [red]✗[/red]  {msg}\n")


# ── 업로드 ────────────────────────────────────────────────

def get_uploaders(config: dict, platforms: tuple) -> list:
    return [PLATFORM_MAP[n][0](config.get(PLATFORM_MAP[n][1], {})) for n in platforms]


def run_upload(config: dict, platforms: tuple, post_yaml: str):
    content   = ContentManager.from_yaml(post_yaml)
    uploaders = get_uploaders(config, platforms)
    results   = []

    with console.status("  업로드 중...", spinner="dots"):
        for uploader in uploaders:
            results.append(uploader.upload(content))

    print_results(results)
    return results


# ── CLI ──────────────────────────────────────────────────

@click.group()
def cli():
    """소셜미디어 멀티플랫폼 자동 업로드 도구"""
    _header()


@cli.command()
@click.argument("post_yaml")
@click.option("--platforms", "-p", multiple=True,
              type=click.Choice(list(PLATFORM_MAP.keys())),
              default=list(PLATFORM_MAP.keys()), show_default=True)
@click.option("--config", "-c", default="config.yaml")
def upload(post_yaml: str, platforms: tuple, config: str):
    """포스트 YAML 파일을 지정한 플랫폼에 업로드합니다.

    예시: python main.py upload posts/my_post.yaml -p instagram -p threads
    """
    cfg = load_config(config)
    run_upload(cfg, platforms or tuple(PLATFORM_MAP.keys()), post_yaml)


@cli.command()
@click.argument("post_yaml")
@click.argument("schedule_time")
@click.option("--platforms", "-p", multiple=True,
              type=click.Choice(list(PLATFORM_MAP.keys())),
              default=list(PLATFORM_MAP.keys()))
@click.option("--config", "-c", default="config.yaml")
def schedule(post_yaml: str, schedule_time: str, platforms: tuple, config: str):
    """특정 시각에 예약 업로드합니다.  형식: 2024-12-01T09:00:00

    예시: python main.py schedule posts/my_post.yaml 2024-12-01T09:00 -p instagram
    """
    cfg = load_config(config)
    scheduler = PostScheduler(timezone=cfg.get("scheduler", {}).get("timezone", "Asia/Seoul"))
    scheduler.add_once(run_upload, schedule_time, cfg, platforms, post_yaml)
    _ok(f"예약 등록 완료  [dim]{schedule_time}[/dim]")
    scheduler.start()


@cli.command()
@click.argument("post_yaml")
@click.argument("cron_expr")
@click.option("--platforms", "-p", multiple=True,
              type=click.Choice(list(PLATFORM_MAP.keys())),
              default=list(PLATFORM_MAP.keys()))
@click.option("--config", "-c", default="config.yaml")
def schedule_recurring(post_yaml: str, cron_expr: str, platforms: tuple, config: str):
    """Cron 표현식으로 반복 업로드를 예약합니다.

    예시: python main.py schedule-recurring posts/my_post.yaml "0 9 * * *" -p instagram
    """
    cfg = load_config(config)
    scheduler = PostScheduler(timezone=cfg.get("scheduler", {}).get("timezone", "Asia/Seoul"))
    scheduler.add_recurring(run_upload, cron_expr, cfg, platforms, post_yaml)
    _ok(f"반복 예약 등록  [dim]{cron_expr}[/dim]")
    scheduler.start()


@cli.command()
@click.option("--output", "-o", default="posts/example_post.yaml")
def new_post(output: str):
    """새 포스트 YAML 템플릿을 생성합니다.

    예시: python main.py new-post -o posts/my_content.yaml
    """
    path = ContentManager.create_template(output)
    _ok(f"템플릿 생성됨  [dim]{path}[/dim]")
    _info("파일을 열어 내용 작성 후 upload 명령으로 업로드하세요.")


@cli.command()
@click.option("--config", "-c", default="config.yaml")
def check_config(config: str):
    """설정 파일의 활성화된 플랫폼을 확인합니다."""
    cfg = load_config(config)
    console.print("  [bold]플랫폼 상태[/bold]")
    console.print()
    for name, (_, config_key) in PLATFORM_MAP.items():
        enabled = cfg.get(config_key, {}).get("enabled", False)
        dot     = "[green]●[/green]" if enabled else "[dim]○[/dim]"
        label   = PLATFORM_LABELS.get(name, name)
        console.print(f"  {dot}  {label}")
    console.print()


# ── AI 콘텐츠 생성 ───────────────────────────────────────

@cli.command()
@click.argument("topic")
@click.option("--platform", "-p",
              type=click.Choice(["instagram", "youtube", "blog", "threads", "all"]),
              default="all")
@click.option("--hashtags", "-ht", is_flag=True, default=True)
@click.option("--save", "-s", default=None)
@click.option("--config", "-c", default="config.yaml")
def generate(topic: str, platform: str, hashtags: bool, save: str, config: str):
    """ChatGPT로 포스트를 자동 생성합니다.

    예시: python main.py generate "AI 마케팅" -p instagram --save posts/ai.yaml
    """
    cfg = load_config(config)
    ai_config = cfg.get("openai", {})

    if not ai_config.get("enabled"):
        _err("OpenAI 비활성화  [dim]→ config.yaml에서 openai.enabled: true 설정[/dim]")
        return

    try:
        with console.status(f"  생성 중: {topic}...", spinner="dots"):
            generator = AIContentGenerator(ai_config)
            content   = generator.generate_post(topic, platform, hashtags)

        console.print()
        console.print(f"  [dim]제목[/dim]    {content.title}")
        console.print(f"  [dim]본문[/dim]    {content.body}")
        console.print(f"  [dim]태그[/dim]    {', '.join(content.tags)}")
        console.print(f"  [dim]해시태그[/dim] {' '.join(content.hashtags)}")
        console.print()

        if save:
            import yaml
            from pathlib import Path
            output_path = save if save.endswith(".yaml") else f"{save}.yaml"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump({
                    "title": content.title, "body": content.body,
                    "tags": content.tags,   "hashtags": content.hashtags,
                    "image_paths": [],      "video_path": None, "schedule_time": None,
                }, f, allow_unicode=True, default_flow_style=False)
            _ok(f"저장됨  [dim]{output_path}[/dim]")
            _info(f"python main.py upload {output_path}")

    except Exception as e:
        _err(str(e))


@cli.command()
@click.argument("topic")
@click.option("--platforms", "-p", multiple=True,
              type=click.Choice(["instagram", "youtube", "blog", "threads"]),
              default=["instagram", "threads", "youtube", "blog"])
@click.option("--save-dir", "-d", default="posts")
@click.option("--config",   "-c", default="config.yaml")
def generate_batch(topic: str, platforms: tuple, save_dir: str, config: str):
    """여러 플랫폼용 포스트를 한 번에 생성합니다.

    예시: python main.py generate-batch "AI 마케팅" -p instagram -p youtube
    """
    cfg = load_config(config)
    ai_config = cfg.get("openai", {})

    if not ai_config.get("enabled"):
        _err("OpenAI 비활성화  [dim]→ config.yaml에서 openai.enabled: true 설정[/dim]")
        return

    try:
        with console.status(f"  생성 중: {topic}...", spinner="dots"):
            generator = AIContentGenerator(ai_config)
            contents  = generator.batch_generate(topic, list(platforms) or None)

        import yaml
        from pathlib import Path
        Path(save_dir).mkdir(parents=True, exist_ok=True)

        console.print()
        for plat, content in contents.items():
            filename = f"{save_dir}/{plat}_{topic.replace(' ', '_')}.yaml"
            with open(filename, "w", encoding="utf-8") as f:
                yaml.dump({
                    "title": content.title, "body": content.body,
                    "tags": content.tags,   "hashtags": content.hashtags,
                    "image_paths": [],      "video_path": None, "schedule_time": None,
                }, f, allow_unicode=True, default_flow_style=False)
            console.print(f"  [green]✓[/green]  [dim]{filename}[/dim]")

        console.print()
        _ok(f"{len(contents)}개 플랫폼 포스트 생성 완료")

    except Exception as e:
        _err(str(e))


# ── 이미지 생성 ──────────────────────────────────────────

@cli.command()
@click.argument("prompt")
@click.option("--count",    "-n", default=1)
@click.option("--save-dir", "-d", default="assets/images")
@click.option("--config",   "-c", default="config.yaml")
def generate_image(prompt: str, count: int, save_dir: str, config: str):
    """DALL-E로 이미지를 생성합니다.

    예시: python main.py generate-image "미래지향적 AI 이미지" --count 3
    """
    cfg = load_config(config)
    img_config = cfg.get("image_generation", {})

    if not img_config.get("enabled"):
        _err("이미지 생성 비활성화  [dim]→ config.yaml에서 image_generation.enabled: true 설정[/dim]")
        return

    try:
        with console.status(f"  이미지 생성 중 ({count}개)...", spinner="dots"):
            generator = AIImageGenerator(img_config)
            paths = generator.generate_image(prompt, num_images=count, save_dir=save_dir)

        console.print()
        for path in paths:
            console.print(f"  [green]✓[/green]  [dim]{path}[/dim]")
        console.print()
        _ok(f"{len(paths)}개 이미지 저장 완료")

    except Exception as e:
        _err(str(e))


@cli.command()
@click.argument("topic")
@click.option("--cards",    "-n", default=3)
@click.option("--save-dir", "-d", default="assets/images")
@click.option("--config",   "-c", default="config.yaml")
def generate_cardnews(topic: str, cards: int, save_dir: str, config: str):
    """카드뉴스 이미지 시리즈를 자동 생성합니다.

    예시: python main.py generate-cardnews "소셜미디어 마케팅" --cards 4
    """
    cfg = load_config(config)
    img_config = cfg.get("image_generation", {})

    if not img_config.get("enabled"):
        _err("이미지 생성 비활성화  [dim]→ config.yaml에서 image_generation.enabled: true 설정[/dim]")
        return

    try:
        with console.status(f"  카드뉴스 생성 중 ({cards}장)...", spinner="dots"):
            generator = AIImageGenerator(img_config)
            paths = generator.generate_cardnews(topic, num_cards=cards, save_dir=save_dir)

        console.print()
        for idx, path in enumerate(paths, 1):
            console.print(f"  [green]✓[/green]  카드 {idx}  [dim]{path}[/dim]")
        console.print()
        _ok(f"{len(paths)}장 카드뉴스 생성 완료")
        _info("python main.py upload posts/example.yaml -p instagram")

    except Exception as e:
        _err(str(e))


@cli.command()
@click.argument("title")
@click.option("--save-dir", "-d", default="assets/images")
@click.option("--config",   "-c", default="config.yaml")
def generate_thumbnail(title: str, save_dir: str, config: str):
    """YouTube 썸네일을 자동 생성합니다.

    예시: python main.py generate-thumbnail "ChatGPT 마케팅 가이드"
    """
    cfg = load_config(config)
    img_config = cfg.get("image_generation", {})

    if not img_config.get("enabled"):
        _err("이미지 생성 비활성화  [dim]→ config.yaml에서 image_generation.enabled: true 설정[/dim]")
        return

    try:
        with console.status("  썸네일 생성 중...", spinner="dots"):
            generator = AIImageGenerator(img_config)
            path = generator.generate_thumbnail(title, save_dir=save_dir)

        _ok(f"썸네일 생성됨  [dim]{path}[/dim]")

    except Exception as e:
        _err(str(e))


@cli.command()
@click.argument("topic")
@click.option("--cards",     "-c", default=3)
@click.option("--platforms", "-p", multiple=True,
              type=click.Choice(["instagram", "youtube", "blog", "threads"]),
              default=["instagram", "threads"])
@click.option("--save-dir",  "-d", default="posts")
@click.option("--config",          default="config.yaml")
def generate_complete(topic: str, cards: int, platforms: tuple, save_dir: str, config: str):
    """포스트 + 이미지를 한 번에 생성합니다.

    예시: python main.py generate-complete "소셜미디어 트렌드" --cards 3 -p instagram
    """
    cfg = load_config(config)
    ai_config  = cfg.get("openai", {})
    img_config = cfg.get("image_generation", {})

    if not ai_config.get("enabled"):
        _err("Gemini 비활성화  [dim]→ config.yaml에서 openai.enabled: true 설정[/dim]")
        return

    try:
        import yaml
        from pathlib import Path
        Path(save_dir).mkdir(parents=True, exist_ok=True)

        with console.status("  1/3  포스트 생성 중...", spinner="dots") as s:
            text_gen  = AIContentGenerator(ai_config)
            contents  = text_gen.batch_generate(topic, list(platforms) or None)

            s.update("  2/3  이미지 생성 중...")
            img_gen     = AIImageGenerator(img_config)
            image_paths = img_gen.generate_cardnews(topic, num_cards=cards, save_dir="assets/images")

            s.update("  3/3  파일 저장 중...")
            for plat, content in contents.items():
                filename = f"{save_dir}/{plat}_{topic.replace(' ', '_')}.yaml"
                with open(filename, "w", encoding="utf-8") as f:
                    yaml.dump({
                        "title": content.title, "body": content.body,
                        "tags": content.tags,   "hashtags": content.hashtags,
                        "image_paths": image_paths, "video_path": None, "schedule_time": None,
                    }, f, allow_unicode=True, default_flow_style=False)

        console.print()
        for plat in contents:
            filename = f"{save_dir}/{plat}_{topic.replace(' ', '_')}.yaml"
            console.print(f"  [green]✓[/green]  [dim]{filename}[/dim]")
        console.print()
        _ok(f"완료  [dim]{len(contents)}개 플랫폼 · {len(image_paths)}장 이미지[/dim]")
        _info(f"python main.py upload {save_dir}/instagram_{topic.replace(' ', '_')}.yaml -p instagram -p threads")

    except Exception as e:
        _err(str(e))


if __name__ == "__main__":
    cli()
