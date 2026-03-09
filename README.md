# bilibili-cli

A CLI for Bilibili — browse videos, users, favorites from the terminal 📺

[English](#features) | [中文](#功能特性)

## More Projects

- [xhs-cli](https://github.com/jackwener/xhs-cli) — Xiaohongshu CLI tooling
- [twitter-cli](https://github.com/jackwener/twitter-cli) — Twitter/X CLI tooling

## Features

- 🎬 **Video** — details, subtitles, AI summary, comments, related videos
- 🎵 **Audio** — extract audio and split into ASR-ready WAV segments
- 👤 **User** — profile, video list, following list
- 🔍 **Search** — search users or videos by keyword
- 🔥 **Trending** — hot videos and site-wide ranking
- 📰 **Feed** — dynamic timeline from your follows
- 📂 **Favorites** — browse favorite folders, watch-later, and watch history
- 👍 **Interactions** — like, coin, triple (一键三连)
- 🔐 **Smart auth** — auto-extracts cookies from Chrome/Firefox, or QR code login
- 📊 **JSON output** — major query commands support `--json` for scripting

## Installation

```bash
# Recommended: uv tool (fast, isolated)
uv tool install bilibili-cli

# Or: pipx
pipx install bilibili-cli

# If you need audio extraction support
uv tool install "bilibili-cli[audio]"
# or
pipx install "bilibili-cli[audio]"
```

Or from source:

```bash
git clone git@github.com:jackwener/bilibili-cli.git
cd bilibili-cli
uv sync
```

Run tests in the project environment:

```bash
uv run pytest -q
uv run ruff check .
uv run mypy bili_cli
```

## Usage

```bash
# Login & account
bili status                    # Check login status
bili login                     # QR code login
bili whoami                    # Detailed profile (level, coins, followers)

# Videos
bili video BV1ABcsztEcY                 # Video details
bili video BV1ABcsztEcY --subtitle                 # With subtitles (plain text)
bili video BV1ABcsztEcY --subtitle-timeline        # With timeline
bili video BV1ABcsztEcY -st --subtitle-format srt  # Export as SRT format
bili video BV1ABcsztEcY --ai            # AI summary
bili video BV1ABcsztEcY --comments      # Top comments
bili video BV1ABcsztEcY --related       # Related videos
bili video BV1ABcsztEcY --json          # Raw JSON

# Users
bili user 946974                        # UP profile
bili user "影视飓风"                     # Search by name
bili user-videos 946974 --max 20        # Video list

# Discovery
bili hot                                # Trending videos (page 1)
bili hot --page 2 --max 10              # Page 2, top 10
bili rank                               # Site-wide ranking (3-day)
bili rank --day 7 --max 30              # 7-day ranking, top 30
bili search "关键词"                     # Search users
bili search "关键词" --type video --max 5 # Search videos (top 5)
bili search "关键词" --page 2            # Next page
bili feed                               # Dynamic timeline
bili feed --offset 1234567890           # Next page via returned cursor
bili my-dynamics                         # My posted dynamics
bili dynamic-post "抽个奖，明天开奖"       # Publish text dynamic
bili dynamic-delete 123456789012345678   # Delete one dynamic

# Collections
bili favorites                          # Favorite folders
bili favorites <ID> --page 2            # Videos in a folder
bili following                          # Following list
bili watch-later                        # Watch later
bili history                            # Watch history

# Audio extraction
bili audio BV1ABcsztEcY                 # Download + split into 25s WAV segments
bili audio BV1ABcsztEcY --segment 60    # 60s per segment
bili audio BV1ABcsztEcY --no-split      # Full m4a, no splitting
bili audio BV1ABcsztEcY -o ~/data/      # Custom output directory

# Interactions
bili like BV1ABcsztEcY                  # Like
bili coin BV1ABcsztEcY                  # Give coin
bili triple BV1ABcsztEcY                # 一键三连 🎉
bili unfollow 946974                    # Unfollow by UID
```

## Authentication

bilibili-cli uses a 3-tier authentication strategy:

1. **Saved credential** — loads from `~/.bilibili-cli/credential.json`
2. **Browser cookies** — auto-extracts from Chrome, Firefox, Edge, or Brave
3. **QR code login** — `bili login` displays a QR code in the terminal

Credentials are validated on use for authenticated commands. Expired cookies are automatically cleared, while transient network validation failures keep local credentials for best-effort fallback.
`bili status` exits with code `0` only when authenticated; otherwise it exits with `1`.

Most commands work without login. Subtitles, favorites/following/watch-later/history, feed, my-dynamics, and interactions require authentication. Write actions (like/coin/triple/unfollow/dynamic-post/dynamic-delete) require write-capable credential (`bili_jct`).

Audio extraction requires the optional `audio` dependency group (`av`).

## Use as AI Agent Skill

bilibili-cli ships with a [`SKILL.md`](./SKILL.md) that teaches AI agents how to use it.

### Claude Code / Antigravity

```bash
# Clone into your project's skills directory
mkdir -p .agents/skills
git clone git@github.com:jackwener/bilibili-cli.git .agents/skills/bilibili-cli

# Or just copy the SKILL.md
curl -o .agents/skills/bilibili-cli/SKILL.md \
  https://raw.githubusercontent.com/jackwener/bilibili-cli/main/SKILL.md
```

Once added, AI agents that support the `.agents/skills/` convention will automatically discover and use bilibili-cli commands.

### OpenClaw / ClawHub

Officially supports [OpenClaw](https://openclaw.ai) and [ClawHub](https://docs.openclaw.ai/tools/clawhub). Install via ClawHub:

```bash
clawhub install bilibili-cli
```

All bilibili-cli commands are available in OpenClaw after installation.

---

## 推荐项目

- [xhs-cli](https://github.com/jackwener/xhs-cli) — 小红书 CLI 工具
- [twitter-cli](https://github.com/jackwener/twitter-cli) — Twitter/X CLI 工具

## 功能特性

- 🎬 **视频** — 详情、字幕、AI 总结、评论、相关推荐
- 🎵 **音频** — 提取视频音频，切分为语音识别 (ASR) 可用的 WAV 片段
- 👤 **用户** — UP 主资料、视频列表、关注列表
- 🔍 **搜索** — 按关键词搜索用户或视频
- 🔥 **发现** — 热门视频、全站排行榜
- 📰 **动态** — 关注的人的动态时间线
- 📂 **收藏** — 收藏夹浏览、稍后再看、观看历史
- 👍 **互动** — 点赞、投币、一键三连
- 🔐 **智能认证** — 自动提取浏览器 Cookie，或扫码登录
- 📊 **JSON 输出** — 主要查询命令支持 `--json`，方便脚本调用

## 安装

```bash
# 推荐：uv tool（快速、隔离环境）
uv tool install bilibili-cli

# 或者：pipx
pipx install bilibili-cli

# 如果需要音频提取功能
uv tool install "bilibili-cli[audio]"
# 或
pipx install "bilibili-cli[audio]"
```

或从源码安装：

```bash
git clone git@github.com:jackwener/bilibili-cli.git
cd bilibili-cli
uv sync
```

## 使用示例

```bash
# 登录与账号
bili status                    # 检查登录状态
bili login                     # 扫码登录
bili whoami                    # 查看个人信息（等级、硬币、粉丝数）

# 视频
bili video BV1ABcsztEcY                 # 视频详情
bili video BV1ABcsztEcY --subtitle                 # 显示字幕（纯文本）
bili video BV1ABcsztEcY --subtitle-timeline        # 显示带时间线的字幕
bili video BV1ABcsztEcY -st --subtitle-format srt  # 导出为 SRT 格式
bili video BV1ABcsztEcY --ai            # AI 总结
bili video BV1ABcsztEcY --comments      # 热门评论
bili video BV1ABcsztEcY --related       # 相关推荐

# 用户
bili user 946974                        # UP 主资料
bili user "影视飓风"                     # 按用户名搜索
bili user-videos 946974 --max 20        # 视频列表

# 发现
bili hot                                # 热门视频（第1页）
bili hot --page 2 --max 10              # 第2页，前10条
bili rank                               # 全站排行榜（3日）
bili rank --day 7 --max 30              # 7日榜，前30条
bili search "关键词"                     # 搜索用户
bili search "关键词" --type video --max 5 # 搜索视频（前5条）
bili search "关键词" --page 2            # 第2页结果
bili feed                               # 动态时间线
bili feed --offset 1234567890           # 使用上一页游标翻页
bili my-dynamics                         # 我发布的动态
bili dynamic-post "抽个奖，明天开奖"       # 发布文字动态
bili dynamic-delete 123456789012345678   # 删除单条动态

# 收藏
bili favorites                          # 收藏夹列表
bili following                          # 关注列表
bili watch-later                        # 稍后再看
bili history                            # 观看历史

# 音频提取
bili audio BV1ABcsztEcY                 # 下载并切分为 25 秒 WAV 片段
bili audio BV1ABcsztEcY --segment 60    # 每段 60 秒
bili audio BV1ABcsztEcY --no-split      # 完整 m4a，不切分
bili audio BV1ABcsztEcY -o ~/data/      # 自定义输出目录

# 互动
bili like BV1ABcsztEcY                  # 点赞
bili coin BV1ABcsztEcY                  # 投币
bili triple BV1ABcsztEcY                # 一键三连 🎉
bili unfollow 946974                    # 取消关注（按 UID）
```

## 认证策略

bilibili-cli 采用三级认证策略：

1. **已保存凭证** — 从 `~/.bilibili-cli/credential.json` 加载
2. **浏览器 Cookie** — 自动从 Chrome、Firefox、Edge、Brave 提取
3. **扫码登录** — `bili login` 在终端显示二维码

需要认证的命令会自动校验凭证。过期 Cookie 会自动清除；如果只是临时网络异常，不会误清本地凭证（会以 best-effort 继续尝试）。

大部分命令无需登录。字幕、收藏夹、动态和互动操作需要登录。写操作（like/coin/triple/unfollow/dynamic-post/dynamic-delete）需要可写凭证（包含 `bili_jct`）。

音频提取功能需要安装可选依赖组 `audio`（即 `av`）。

## 作为 AI Agent Skill 使用

bilibili-cli 自带 [`SKILL.md`](./SKILL.md)，让 AI Agent 能自动学习并使用本工具。

### Claude Code / Antigravity

```bash
# 克隆到项目的 skills 目录
mkdir -p .agents/skills
git clone git@github.com:jackwener/bilibili-cli.git .agents/skills/bilibili-cli

# 或者只复制 SKILL.md
curl -o .agents/skills/bilibili-cli/SKILL.md \
  https://raw.githubusercontent.com/jackwener/bilibili-cli/main/SKILL.md
```

添加后，支持 `.agents/skills/` 的 AI Agent 会自动发现并使用 bilibili-cli 命令。

### OpenClaw / ClawHub

官方支持 [OpenClaw](https://openclaw.ai) 和 [ClawHub](https://docs.openclaw.ai/tools/clawhub) 生态。通过 ClawHub 安装：

```bash
clawhub install bilibili-cli
```

安装后即可在 OpenClaw 中直接使用所有 bilibili-cli 命令。

## License

Apache-2.0
