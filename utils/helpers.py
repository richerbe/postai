import yaml
from pathlib import Path
from rich.console import Console
from platforms.base import UploadResult

console = Console()


def load_config(config_path: str = "config.yaml") -> dict:
    p = Path(config_path)
    if not p.exists():
        console.print(f"[red]✗[/red]  설정 파일 없음: [dim]{config_path}[/dim]")
        console.print(f"   [dim]config.yaml을 생성하고 API 키를 입력하세요.[/dim]")
        raise FileNotFoundError(f"설정 파일 없음: {config_path}")
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def print_results(results: list[UploadResult]):
    console.print()
    for r in results:
        if r.success:
            detail = f"[dim]{r.url or '—'}[/dim]"
            console.print(f"  [green]✓[/green]  {r.platform:<16}{detail}")
        else:
            detail = f"[dim]{r.error or '알 수 없는 오류'}[/dim]"
            console.print(f"  [red]✗[/red]  {r.platform:<16}{detail}")

    success = sum(1 for r in results if r.success)
    total   = len(results)
    color   = "green" if success == total else ("yellow" if success > 0 else "red")
    console.print()
    console.print(f"  [{color}]{success}/{total} 성공[/{color}]")
    console.print()
