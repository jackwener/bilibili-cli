# bilibili-cli

A CLI for Bilibili — browse videos, users, favorites from the terminal 📺

[English](#features) | [中文](#功能特性)

## Features

- 🎬 **Video** — details, subtitles, AI summary, comments, related videos
- 👤 **User** — profile, video list, following list
- 🔍 **Search** — search users or videos by keyword
- � **Trending** — hot videos and site-wide ranking
- 📰 **Feed** — dynamic timeline from your follows
- �📂 **Favorites** — browse favorite folders and watch-later list
- 👍 **Interactions** — like, coin, triple (一键三连)
- 🔐 **Smart auth** — auto-extracts cookies from Chrome/Firefox, or QR code login
- 📊 **JSON output** — all commands support `--json` for scripting

## Installation

```bash
# Recommended: pipx (auto-manages virtualenv)
pipx install bilibili-cli

# Or: uv tool
uv tool install bilibili-cli
```

Or from source:

```bash
git clone git@github.com:jackwener/bilibili-cli.git
cd bilibili-cli
uv sync
```

## Usage

```bash
# Login & account
bili status                    # Check login status
bili login                     # QR code login
bili whoami                    # Detailed profile (level, coins, followers)

# Videos
bili video BV1ABcsztEcY                 # Video details
bili video BV1ABcsztEcY --subtitle      # With subtitles
bili video BV1ABcsztEcY --ai            # AI summary
bili video BV1ABcsztEcY --comments      # Top comments
bili video BV1ABcsztEcY --related       # Related videos
bili video BV1ABcsztEcY --json          # Raw JSON

# Users
bili user 946974                        # UP profile
bili user "影视飓风"                     # Search by name
bili user-videos 946974 --max 20        # Video list

# Discovery
bili hot                                # Trending videos
bili rank                               # Site-wide ranking
bili search "关键词"                     # Search users
bili search "关键词" --type video        # Search videos
bili feed                               # Dynamic timeline

# Collections
bili favorites                          # Favorite folders
bili favorites <ID> --page 2            # Videos in a folder
bili following                          # Following list
bili history                            # Watch later

# Interactions
bili like BV1ABcsztEcY                  # Like
bili coin BV1ABcsztEcY                  # Give coin
bili triple BV1ABcsztEcY                # 一键三连 🎉
```

## Authentication

bilibili-cli uses a 3-tier authentication strategy:

1. **Saved credential** — loads from `~/.bilibili-cli/credential.json`
2. **Browser cookies** — auto-extracts from Chrome, Firefox, Edge, or Brave
3. **QR code login** — `bili login` displays a QR code in the terminal

Credentials are validated on each use. Expired cookies are automatically cleared.

Most commands work without login. Subtitles, favorites, feed, and interactions require authentication.

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

## 功能特性

- 🎬 **视频** — 详情、字幕、AI 总结、评论、相关推荐
- 👤 **用户** — UP 主资料、视频列表、关注列表
- 🔍 **搜索** — 按关键词搜索用户或视频
- 🔥 **发现** — 热门视频、全站排行榜
- 📰 **动态** — 关注的人的动态时间线
- 📂 **收藏** — 收藏夹浏览、稍后再看
- 👍 **互动** — 点赞、投币、一键三连
- 🔐 **智能认证** — 自动提取浏览器 Cookie，或扫码登录
- 📊 **JSON 输出** — 所有命令支持 `--json`，方便脚本调用

## 安装

```bash
# 推荐：pipx（自动管理虚拟环境）
pipx install bilibili-cli

# 或者：uv tool
uv tool install bilibili-cli
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
bili video BV1ABcsztEcY --subtitle      # 显示字幕
bili video BV1ABcsztEcY --ai            # AI 总结
bili video BV1ABcsztEcY --comments      # 热门评论
bili video BV1ABcsztEcY --related       # 相关推荐

# 用户
bili user 946974                        # UP 主资料
bili user "影视飓风"                     # 按用户名搜索
bili user-videos 946974 --max 20        # 视频列表

# 发现
bili hot                                # 热门视频
bili rank                               # 全站排行榜
bili search "关键词"                     # 搜索用户
bili search "关键词" --type video        # 搜索视频
bili feed                               # 动态时间线

# 收藏
bili favorites                          # 收藏夹列表
bili following                          # 关注列表
bili history                            # 稍后再看

# 互动
bili like BV1ABcsztEcY                  # 点赞
bili coin BV1ABcsztEcY                  # 投币
bili triple BV1ABcsztEcY                # 一键三连 🎉
```

## 认证策略

bilibili-cli 采用三级认证策略：

1. **已保存凭证** — 从 `~/.bilibili-cli/credential.json` 加载
2. **浏览器 Cookie** — 自动从 Chrome、Firefox、Edge、Brave 提取
3. **扫码登录** — `bili login` 在终端显示二维码

凭证在每次使用时自动验证，过期 Cookie 会自动清除。

大部分命令无需登录。字幕、收藏夹、动态和互动操作需要登录。

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
