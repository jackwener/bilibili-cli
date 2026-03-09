"""Video related command."""

from __future__ import annotations

import json

import click
from rich.table import Table

from . import common


@click.command()
@click.argument("bv_or_url")
@click.option("--subtitle", "-s", is_flag=True, help="显示字幕内容（纯文本）。")
@click.option("--subtitle-timeline", "-st", is_flag=True, help="显示带时间线的字幕。")
@click.option("--subtitle-format", type=click.Choice(["timeline", "srt"]), default="timeline", help="字幕格式：timeline（人类可读）或 srt。")
@click.option("--comments", "-c", is_flag=True, help="显示评论。")
@click.option("--ai", is_flag=True, help="显示 AI 总结。")
@click.option("--related", "-r", is_flag=True, help="显示相关推荐视频。")
@click.option("--json", "as_json", is_flag=True, help="输出原始 JSON。")
def video(bv_or_url: str, subtitle: bool, subtitle_timeline: bool, subtitle_format: str, comments: bool, ai: bool, related: bool, as_json: bool):
    """查看视频详情。

    BV_OR_URL 可以是 BV 号（如 BV1xxx）或完整 URL。
    """
    from .. import client

    bvid = common.extract_bvid_or_exit(bv_or_url)
    needs_optional_cred = subtitle or comments or ai or related
    cred = common.get_credential(mode="optional") if needs_optional_cred else None

    info = common.run_or_exit(
        client.get_video_info(bvid, credential=None),
        "获取视频信息失败",
    )

    if as_json:
        click.echo(json.dumps(info, ensure_ascii=False, indent=2))
        return

    stat = info.get("stat", {})
    owner = info.get("owner", {})

    table = Table(title=f"📺 {info.get('title', bvid)}", show_header=False, border_style="blue")
    table.add_column("Field", style="bold cyan", width=12)
    table.add_column("Value")

    table.add_row("BV号", bvid)
    table.add_row("标题", info.get("title", ""))
    table.add_row("UP主", f"{owner.get('name', '')}  (UID: {owner.get('mid', '')})")
    table.add_row("时长", common.format_duration(info.get("duration", 0)))
    table.add_row("播放", common.format_count(stat.get("view", 0)))
    table.add_row("弹幕", common.format_count(stat.get("danmaku", 0)))
    table.add_row("点赞", common.format_count(stat.get("like", 0)))
    table.add_row("投币", common.format_count(stat.get("coin", 0)))
    table.add_row("收藏", common.format_count(stat.get("favorite", 0)))
    table.add_row("分享", common.format_count(stat.get("share", 0)))
    table.add_row("链接", f"https://www.bilibili.com/video/{bvid}")

    desc = info.get("desc", "").strip()
    if desc:
        table.add_row("简介", desc[:200])

    common.console.print(table)

    if subtitle or subtitle_timeline:
        common.console.print("\n[bold]📝 字幕内容:[/bold]\n")
        sub_data = common.run_optional(
            client.get_video_subtitle(bvid, credential=cred),
            "获取字幕失败",
        )
        if sub_data is not None:
            sub_text, raw = sub_data
            # Determine content to display
            display_content = ""
            if subtitle_timeline and raw:
                display_content = client.format_subtitle_timeline(raw, format=subtitle_format)
            elif subtitle:
                display_content = sub_text
            
            if display_content:
                common.console.print(display_content)
            else:
                common.console.print("[yellow]⚠️  无字幕（可能需要登录或视频无字幕）[/yellow]")

    if ai:
        common.console.print("\n[bold]🤖 AI 总结:[/bold]\n")
        ai_data = common.run_optional(
            client.get_video_ai_conclusion(bvid, credential=cred),
            "获取 AI 总结失败",
        )
        if ai_data is not None:
            summary = ai_data.get("model_result", {}).get("summary", "")
            if summary:
                common.console.print(summary)
            else:
                common.console.print("[yellow]⚠️  该视频暂无 AI 总结[/yellow]")

    if comments:
        common.console.print("\n[bold]💬 热门评论:[/bold]\n")
        cm_data = common.run_optional(
            client.get_video_comments(bvid, credential=cred),
            "获取评论失败",
        )
        if cm_data is not None:
            replies = cm_data.get("replies") or []
            if not replies:
                common.console.print("[yellow]暂无评论[/yellow]")
            else:
                for c in replies[:10]:
                    member = c.get("member", {})
                    content = c.get("content", {}).get("message", "")
                    likes = c.get("like", 0)
                    uname = member.get("uname", "")
                    common.console.print(f"  [cyan]{uname}[/cyan]  [dim](👍 {likes})[/dim]")
                    common.console.print(f"  {content[:120]}")
                    common.console.print()

    if related:
        common.console.print()
        rel_list = common.run_optional(
            client.get_related_videos(bvid, credential=cred),
            "获取相关推荐失败",
        )
        if rel_list:
            table = Table(title="📎 相关推荐", border_style="blue")
            table.add_column("#", style="dim", width=4)
            table.add_column("BV号", style="cyan", width=14)
            table.add_column("标题", max_width=40)
            table.add_column("UP主", width=12)
            table.add_column("播放", width=8, justify="right")

            for i, rv in enumerate(rel_list[:10], 1):
                ro = rv.get("owner", {})
                rs = rv.get("stat", {})
                table.add_row(
                    str(i),
                    rv.get("bvid", ""),
                    rv.get("title", "")[:40],
                    ro.get("name", "")[:12],
                    common.format_count(rs.get("view", 0)),
                )
            common.console.print(table)
