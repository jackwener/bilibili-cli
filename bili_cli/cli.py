"""CLI entry point for bilibili-cli.

Usage:
    bili login
    bili status
    bili video <BV号或URL> [--subtitle] [--json]
    bili user <UID或用户名> [--count N] [--json]
    bili search <关键词> [--json]
    bili favorites [收藏夹ID] [--page N] [--json]
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from . import __version__
from .auth import get_credential, qr_login, clear_credential

console = Console()


def _run(coro):
    """Bridge async coroutine into synchronous click command."""
    return asyncio.run(coro)


def _setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(name)s: %(message)s")


def _format_duration(seconds: int) -> str:
    """Format seconds into MM:SS or HH:MM:SS."""
    if seconds >= 3600:
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h}:{m:02d}:{s:02d}"
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"


def _format_count(n: int) -> str:
    """Format large numbers with 万 suffix."""
    if n >= 10000:
        return f"{n / 10000:.1f}万"
    return str(n)


# ===== Main Group =====


@click.group()
@click.version_option(version=__version__, prog_name="bili")
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
def cli(verbose: bool):
    """bili — Bilibili CLI tool 📺"""
    _setup_logging(verbose)


# ===== Login =====


@cli.command()
def login():
    """扫码登录 Bilibili。"""
    try:
        _run(qr_login())
    except RuntimeError as e:
        console.print(f"[red]❌ {e}[/red]")
        sys.exit(1)


@cli.command()
def logout():
    """注销并清除保存的凭证。"""
    clear_credential()
    console.print("[green]✅ 已注销，凭证已清除[/green]")


@cli.command()
def status():
    """检查登录状态。"""
    from . import client

    cred = get_credential()
    if not cred:
        console.print("[yellow]⚠️  未登录。使用 [bold]bili login[/bold] 登录。[/yellow]")
        return

    try:
        info = _run(client.get_self_info(cred))
        uid = info.get("mid", "unknown")
        relation = _run(client.get_user_relation_info(uid, credential=cred))

        name = info.get("name", "unknown")
        level = info.get("level", "?")
        coins = info.get("coins", 0)
        follower = relation.get("follower", 0)
        following = relation.get("following", 0)

        # VIP status
        vip = info.get("vip", {})
        vip_label = ""
        if vip.get("status") == 1:
            vip_type = "大会员" if vip.get("type") == 2 else "小会员"
            vip_label = f"  |  🏅 {vip_type}"

        sign = info.get("sign", "").strip()

        lines = [
            f"👤 [bold]{name}[/bold]  (UID: {uid})",
            f"⭐ Level {level}  |  🪙 硬币 {coins}{vip_label}",
            f"👥 粉丝 {_format_count(follower)}  |  🔔 关注 {_format_count(following)}",
        ]
        if sign:
            lines.append(f"📝 {sign}")

        console.print(Panel(
            "\n".join(lines),
            title="登录状态",
            border_style="green",
        ))
    except Exception as e:
        console.print(f"[red]❌ 凭证可能已过期: {e}[/red]")
        console.print("[yellow]请使用 [bold]bili login[/bold] 重新登录。[/yellow]")


# ===== Video =====


@cli.command()
@click.argument("bv_or_url")
@click.option("--subtitle", "-s", is_flag=True, help="显示字幕内容。")
@click.option("--comments", "-c", is_flag=True, help="显示评论。")
@click.option("--ai", is_flag=True, help="显示 AI 总结。")
@click.option("--related", "-r", is_flag=True, help="显示相关推荐视频。")
@click.option("--json", "as_json", is_flag=True, help="输出原始 JSON。")
def video(bv_or_url: str, subtitle: bool, comments: bool, ai: bool, related: bool, as_json: bool):
    """查看视频详情。

    BV_OR_URL 可以是 BV 号（如 BV1xxx）或完整 URL。
    """
    from . import client

    cred = get_credential()

    try:
        bvid = client.extract_bvid(bv_or_url)
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        sys.exit(1)

    info = _run(client.get_video_info(bvid, credential=cred))

    if as_json:
        click.echo(json.dumps(info, ensure_ascii=False, indent=2))
        return

    # Display video info
    stat = info.get("stat", {})
    owner = info.get("owner", {})

    table = Table(title=f"📺 {info.get('title', bvid)}", show_header=False, border_style="blue")
    table.add_column("Field", style="bold cyan", width=12)
    table.add_column("Value")

    table.add_row("BV号", bvid)
    table.add_row("标题", info.get("title", ""))
    table.add_row("UP主", f"{owner.get('name', '')}  (UID: {owner.get('mid', '')})")
    table.add_row("时长", _format_duration(info.get("duration", 0)))
    table.add_row("播放", _format_count(stat.get("view", 0)))
    table.add_row("弹幕", _format_count(stat.get("danmaku", 0)))
    table.add_row("点赞", _format_count(stat.get("like", 0)))
    table.add_row("投币", _format_count(stat.get("coin", 0)))
    table.add_row("收藏", _format_count(stat.get("favorite", 0)))
    table.add_row("分享", _format_count(stat.get("share", 0)))
    table.add_row("链接", f"https://www.bilibili.com/video/{bvid}")

    desc = info.get("desc", "").strip()
    if desc:
        table.add_row("简介", desc[:200])

    console.print(table)

    # Show subtitle if requested
    if subtitle:
        console.print("\n[bold]📝 字幕内容:[/bold]\n")
        sub_text, _ = _run(client.get_video_subtitle(bvid, credential=cred))
        if sub_text:
            console.print(sub_text)
        else:
            console.print("[yellow]⚠️  无字幕（可能需要登录或视频无字幕）[/yellow]")

    # Show AI conclusion
    if ai:
        console.print("\n[bold]🤖 AI 总结:[/bold]\n")
        try:
            ai_data = _run(client.get_video_ai_conclusion(bvid, credential=cred))
            summary = ai_data.get("model_result", {}).get("summary", "")
            if summary:
                console.print(summary)
            else:
                console.print("[yellow]⚠️  该视频暂无 AI 总结[/yellow]")
        except Exception as e:
            console.print(f"[yellow]⚠️  获取 AI 总结失败: {e}[/yellow]")

    # Show comments
    if comments:
        console.print("\n[bold]💬 热门评论:[/bold]\n")
        try:
            cm_data = _run(client.get_video_comments(bvid, credential=cred))
            replies = cm_data.get("replies") or []
            if not replies:
                console.print("[yellow]暂无评论[/yellow]")
            else:
                for c in replies[:10]:
                    member = c.get("member", {})
                    content = c.get("content", {}).get("message", "")
                    likes = c.get("like", 0)
                    uname = member.get("uname", "")
                    console.print(f"  [cyan]{uname}[/cyan]  [dim](👍 {likes})[/dim]")
                    console.print(f"  {content[:120]}")
                    console.print()
        except Exception as e:
            console.print(f"[yellow]⚠️  获取评论失败: {e}[/yellow]")

    # Show related videos
    if related:
        console.print()
        try:
            rel_list = _run(client.get_related_videos(bvid, credential=cred))
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
                        _format_count(rs.get("view", 0)),
                    )
                console.print(table)
        except Exception as e:
            console.print(f"[yellow]⚠️  获取相关推荐失败: {e}[/yellow]")


# ===== User =====


@cli.command()
@click.argument("uid_or_name")
@click.option("--count", "-n", default=10, help="显示的视频数量 (默认 10)。")
@click.option("--json", "as_json", is_flag=True, help="输出原始 JSON。")
def user(uid_or_name: str, count: int, as_json: bool):
    """查看 UP 主信息和最新视频。

    UID_OR_NAME 可以是 UID（纯数字）或用户名（搜索第一个匹配）。
    """
    from . import client

    cred = get_credential()

    # Resolve UID
    if uid_or_name.isdigit():
        uid = int(uid_or_name)
    else:
        # Search by name
        results = _run(client.search_user(uid_or_name))
        if not results:
            console.print(f"[red]❌ 未找到用户: {uid_or_name}[/red]")
            sys.exit(1)
        uid = results[0]["mid"]
        console.print(f"[dim]🔍 匹配到: {results[0].get('uname', '')} (UID: {uid})[/dim]\n")

    # Fetch user info
    try:
        info = _run(client.get_user_info(uid, credential=cred))
        relation = _run(client.get_user_relation_info(uid, credential=cred))
    except Exception as e:
        console.print(f"[red]❌ 获取用户信息失败: {e}[/red]")
        sys.exit(1)

    if as_json:
        videos = _run(client.get_user_videos(uid, count=count, credential=cred))
        output = {"user_info": info, "relation": relation, "videos": videos}
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return

    follower = relation.get("follower", 0)
    following = relation.get("following", 0)

    # Display user info
    console.print(Panel(
        f"👤 [bold]{info.get('name', '')}[/bold]  (UID: {uid})\n"
        f"⭐ Level {info.get('level', '?')}  |  "
        f"👥 粉丝 {_format_count(follower)}  |  "
        f"🔔 关注 {_format_count(following)}",
        title="UP 主信息",
        border_style="cyan",
    ))

    sign = info.get("sign", "").strip()
    if sign:
        console.print(f"[dim]{sign}[/dim]\n")

    # Fetch and display recent videos
    videos = _run(client.get_user_videos(uid, count=count, credential=cred))

    if videos:
        table = Table(title=f"最新 {len(videos)} 个视频", border_style="blue")
        table.add_column("#", style="dim", width=4)
        table.add_column("BV号", style="cyan", width=14)
        table.add_column("标题", max_width=40)
        table.add_column("时长", width=8)
        table.add_column("播放", width=8, justify="right")

        for i, v in enumerate(videos, 1):
            # length from get_videos() is "MM:SS" string, not seconds
            length_raw = v.get("length", "0")
            if isinstance(length_raw, str) and ":" in length_raw:
                length_str = length_raw  # already formatted
            else:
                length_str = _format_duration(int(length_raw) if length_raw else 0)
            table.add_row(
                str(i),
                v.get("bvid", ""),
                v.get("title", "")[:40],
                length_str,
                _format_count(v.get("play", 0)),
            )

        console.print(table)


# ===== Search =====


@cli.command()
@click.argument("keyword")
@click.option("--type", "search_type", default="user", type=click.Choice(["user", "video"]), help="搜索类型 (默认 user)。")
@click.option("--json", "as_json", is_flag=True, help="输出原始 JSON。")
def search(keyword: str, search_type: str, as_json: bool):
    """搜索用户或视频。"""
    from . import client

    if search_type == "video":
        results = _run(client.search_video(keyword))

        if as_json:
            click.echo(json.dumps(results, ensure_ascii=False, indent=2))
            return

        if not results:
            console.print(f"[yellow]未找到与 '{keyword}' 相关的视频[/yellow]")
            return

        table = Table(title=f"🔍 视频搜索: {keyword}", border_style="blue")
        table.add_column("#", style="dim", width=4)
        table.add_column("BV号", style="cyan", width=14)
        table.add_column("标题", max_width=40)
        table.add_column("UP主", width=12)
        table.add_column("播放", width=10, justify="right")
        table.add_column("时长", width=8)

        for i, v in enumerate(results[:20], 1):
            # Clean HTML tags from title
            import re
            title = re.sub(r'<[^>]+>', '', v.get("title", ""))[:40]
            table.add_row(
                str(i),
                v.get("bvid", ""),
                title,
                v.get("author", "")[:12],
                _format_count(v.get("play", 0)),
                v.get("duration", ""),
            )

        console.print(table)
    else:
        results = _run(client.search_user(keyword))

        if as_json:
            click.echo(json.dumps(results, ensure_ascii=False, indent=2))
            return

        if not results:
            console.print(f"[yellow]未找到与 '{keyword}' 相关的用户[/yellow]")
            return

        table = Table(title=f"🔍 搜索: {keyword}", border_style="blue")
        table.add_column("UID", style="cyan", width=12)
        table.add_column("用户名", width=20)
        table.add_column("粉丝", width=10, justify="right")
        table.add_column("视频数", width=8, justify="right")
        table.add_column("签名", max_width=40)

        for u in results[:20]:
            usign = u.get("usign", "")
            table.add_row(
                str(u.get("mid", "")),
                u.get("uname", ""),
                _format_count(u.get("fans", 0)),
                str(u.get("videos", 0)),
                usign[:40] if usign else "",
            )

        console.print(table)


# ===== Favorites =====


@cli.command()
@click.argument("fav_id", required=False, type=int)
@click.option("--page", "-p", default=1, help="页码 (默认 1)。")
@click.option("--json", "as_json", is_flag=True, help="输出原始 JSON。")
def favorites(fav_id: int | None, page: int, as_json: bool):
    """浏览收藏夹。

    不带参数列出所有收藏夹，带 FAV_ID 查看收藏夹内的视频。
    """
    from . import client

    cred = get_credential()
    if not cred:
        console.print("[yellow]⚠️  需要登录才能查看收藏夹。使用 [bold]bili login[/bold] 登录。[/yellow]")
        sys.exit(1)

    if fav_id is None:
        # List all favorite folders
        fav_list = _run(client.get_favorite_list(cred))

        if as_json:
            click.echo(json.dumps(fav_list, ensure_ascii=False, indent=2))
            return

        if not fav_list:
            console.print("[yellow]未找到收藏夹[/yellow]")
            return

        table = Table(title="📂 收藏夹列表", border_style="blue")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("名称", width=20)
        table.add_column("视频数", width=10, justify="right")

        for f in fav_list:
            table.add_row(
                str(f.get("id", "")),
                f.get("title", ""),
                str(f.get("media_count", 0)),
            )

        console.print(table)
        console.print("\n[dim]使用 [bold]bili favorites <ID>[/bold] 查看收藏夹内容[/dim]")

    else:
        # List videos in a specific folder
        data = _run(client.get_favorite_videos(fav_id, cred, page=page))

        if as_json:
            click.echo(json.dumps(data, ensure_ascii=False, indent=2))
            return

        medias = data.get("medias") or []
        if not medias:
            console.print("[yellow]收藏夹为空或不存在[/yellow]")
            return

        table = Table(title=f"📂 收藏夹 #{fav_id}  (第 {page} 页)", border_style="blue")
        table.add_column("#", style="dim", width=4)
        table.add_column("BV号", style="cyan", width=14)
        table.add_column("标题", max_width=40)
        table.add_column("UP主", width=12)
        table.add_column("时长", width=8)

        for i, m in enumerate(medias, 1 + (page - 1) * 20):
            upper = m.get("upper", {})
            table.add_row(
                str(i),
                m.get("bvid", ""),
                (m.get("title", "") or "")[:40],
                (upper.get("name", "") or "")[:12],
                _format_duration(m.get("duration", 0)),
            )

        console.print(table)

        has_more = data.get("has_more", False)
        if has_more:
            console.print(f"\n[dim]还有更多内容，使用 [bold]bili favorites {fav_id} --page {page + 1}[/bold] 查看下一页[/dim]")

# ===== Hot & Rank =====


@cli.command(name="hot")
@click.option("--count", "-n", default=20, help="显示数量 (默认 20)。")
@click.option("--json", "as_json", is_flag=True, help="输出原始 JSON。")
def hot_cmd(count: int, as_json: bool):
    """查看热门视频。"""
    from . import client

    data = _run(client.get_hot_videos(pn=1, ps=count))

    if as_json:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
        return

    vlist = data.get("list") or []
    if not vlist:
        console.print("[yellow]未获取到热门视频[/yellow]")
        return

    table = Table(title="🔥 热门视频", border_style="red")
    table.add_column("#", style="dim", width=4)
    table.add_column("BV号", style="cyan", width=14)
    table.add_column("标题", max_width=36)
    table.add_column("UP主", width=12)
    table.add_column("播放", width=8, justify="right")
    table.add_column("点赞", width=8, justify="right")

    for i, v in enumerate(vlist[:count], 1):
        owner = v.get("owner", {})
        stat = v.get("stat", {})
        table.add_row(
            str(i),
            v.get("bvid", ""),
            v.get("title", "")[:36],
            owner.get("name", "")[:12],
            _format_count(stat.get("view", 0)),
            _format_count(stat.get("like", 0)),
        )

    console.print(table)


@cli.command(name="rank")
@click.option("--json", "as_json", is_flag=True, help="输出原始 JSON。")
def rank_cmd(as_json: bool):
    """查看全站排行榜。"""
    from . import client

    data = _run(client.get_rank_videos())

    if as_json:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
        return

    vlist = data.get("list") or []
    if not vlist:
        console.print("[yellow]未获取到排行榜数据[/yellow]")
        return

    table = Table(title="🏆 全站排行榜", border_style="yellow")
    table.add_column("#", style="bold", width=4)
    table.add_column("BV号", style="cyan", width=14)
    table.add_column("标题", max_width=36)
    table.add_column("UP主", width=12)
    table.add_column("播放", width=8, justify="right")
    table.add_column("综合分", width=8, justify="right")

    for i, v in enumerate(vlist[:20], 1):
        owner = v.get("owner", {})
        stat = v.get("stat", {})
        table.add_row(
            str(i),
            v.get("bvid", ""),
            v.get("title", "")[:36],
            owner.get("name", "")[:12],
            _format_count(stat.get("view", 0)),
            str(v.get("score", "")),
        )

    console.print(table)


# ===== Following =====


@cli.command()
@click.option("--page", "-p", default=1, help="页码 (默认 1)。")
@click.option("--json", "as_json", is_flag=True, help="输出原始 JSON。")
def following(page: int, as_json: bool):
    """查看关注列表。"""
    from . import client

    cred = get_credential()
    if not cred:
        console.print("[yellow]⚠️  需要登录。使用 [bold]bili login[/bold] 登录。[/yellow]")
        sys.exit(1)

    me = _run(client.get_self_info(cred))
    uid = me["mid"]
    data = _run(client.get_followings(uid, pn=page, credential=cred))

    if as_json:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
        return

    flist = data.get("list") or []
    if not flist:
        console.print("[yellow]关注列表为空[/yellow]")
        return

    total = data.get("total", "?")
    table = Table(title=f"🔔 关注列表  (共 {total}, 第 {page} 页)", border_style="blue")
    table.add_column("#", style="dim", width=4)
    table.add_column("UID", style="cyan", width=12)
    table.add_column("用户名", width=16)
    table.add_column("签名", max_width=40)

    for i, u in enumerate(flist, 1 + (page - 1) * 20):
        table.add_row(
            str(i),
            str(u.get("mid", "")),
            u.get("uname", ""),
            (u.get("sign", "") or "")[:40],
        )

    console.print(table)
    console.print(f"\n[dim]使用 [bold]bili following --page {page + 1}[/bold] 查看下一页[/dim]")


# ===== History (Watch Later) =====


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="输出原始 JSON。")
def history(as_json: bool):
    """查看稍后再看列表。"""
    from . import client

    cred = get_credential()
    if not cred:
        console.print("[yellow]⚠️  需要登录。使用 [bold]bili login[/bold] 登录。[/yellow]")
        sys.exit(1)

    try:
        data = _run(client.get_toview(cred))
    except Exception as e:
        console.print(f"[red]❌ 获取稍后再看失败: {e}[/red]")
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
        return

    vlist = data.get("list") or []
    if not vlist:
        console.print("[yellow]稍后再看列表为空[/yellow]")
        return

    count = data.get("count", len(vlist))
    table = Table(title=f"⏰ 稍后再看  (共 {count} 个)", border_style="blue")
    table.add_column("#", style="dim", width=4)
    table.add_column("BV号", style="cyan", width=14)
    table.add_column("标题", max_width=36)
    table.add_column("UP主", width=12)
    table.add_column("时长", width=8)

    for i, v in enumerate(vlist[:30], 1):
        owner = v.get("owner", {})
        table.add_row(
            str(i),
            v.get("bvid", ""),
            v.get("title", "")[:36],
            owner.get("name", "")[:12],
            _format_duration(v.get("duration", 0)),
        )

    console.print(table)


# ===== Dynamic Feed =====


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="输出原始 JSON。")
def feed(as_json: bool):
    """查看动态时间线。"""
    from . import client

    cred = get_credential()
    if not cred:
        console.print("[yellow]⚠️  需要登录。使用 [bold]bili login[/bold] 登录。[/yellow]")
        sys.exit(1)

    try:
        data = _run(client.get_dynamic_feed(credential=cred))
    except Exception as e:
        console.print(f"[red]❌ 获取动态失败: {e}[/red]")
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
        return

    items = data.get("items") or []
    if not items:
        console.print("[yellow]暂无动态[/yellow]")
        return

    console.print("[bold]📰 动态时间线[/bold]\n")

    for item in items[:15]:
        modules = item.get("modules", {})
        author = modules.get("module_author", {})
        dyn_main = modules.get("module_dynamic", {})
        stat = modules.get("module_stat", {})

        name = author.get("name", "")
        pub_time = author.get("pub_time", "")
        dyn_type = item.get("type", "")

        # Extract content based on type
        desc = dyn_main.get("desc", {})
        text = desc.get("text", "") if desc else ""

        major = dyn_main.get("major", {})
        title = ""
        if major:
            archive = major.get("archive", {})
            if archive:
                title = archive.get("title", "")
                bvid = archive.get("bvid", "")
            article = major.get("article", {})
            if article:
                title = article.get("title", "")

        # Comment/like counts
        comment_info = stat.get("comment", {})
        like_info = stat.get("like", {})
        comment_count = comment_info.get("count", 0) if comment_info else 0
        like_count = like_info.get("count", 0) if like_info else 0

        console.print(f"  [cyan]{name}[/cyan]  [dim]{pub_time}[/dim]")
        if title:
            console.print(f"  📺 {title}")
        if text:
            console.print(f"  {text[:100]}")
        if comment_count or like_count:
            console.print(f"  [dim]👍 {like_count}  💬 {comment_count}[/dim]")
        console.print()


if __name__ == "__main__":
    cli()
