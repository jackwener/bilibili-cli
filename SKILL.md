---
name: bilibili-cli
description: CLI skill for Bilibili (哔哩哔哩, B站) to browse videos, users, search, trending, dynamics, favorites, and interactions from the terminal
author: jackwener
version: "1.0.0"
tags:
  - bilibili
  - 哔哩哔哩
  - b站
  - video
  - social-media
  - cli
---

# bilibili-cli Skill

A CLI tool for interacting with Bilibili (哔哩哔哩). Use it to fetch video info, search content, browse user profiles, and perform interactions like liking or triple-clicking.

## Prerequisites

```bash
# Install (requires Python 3.10+)
uv tool install bilibili-cli
# Or: pipx install bilibili-cli

# If you need audio extraction support (requires PyAV)
uv tool install "bilibili-cli[audio]"
# Or: pipx install "bilibili-cli[audio]"
```

## Authentication

Most read commands work without login. Subtitles, favorites/following/watch-later/history, feed, and interactions require login.

```bash
bili status                    # Check if logged in (exit 0 = yes, 1 = no)
bili login                     # QR code login (if not authenticated)
```

Authentication auto-detects local browser cookies (Chrome/Firefox/Edge/Brave). If cookies are found and valid, no manual login needed. Credentials are saved to `~/.bilibili-cli/credential.json`.

## Command Reference

### Video

```bash
# Get video details (accepts BV ID or full URL)
bili video BV1ABcsztEcY
bili video https://www.bilibili.com/video/BV1ABcsztEcY

# Options
bili video BV1ABcsztEcY --subtitle            # Show subtitles (plain text)
bili video BV1ABcsztEcY --subtitle-timeline   # Show subtitles with timestamps
bili video BV1ABcsztEcY -st --subtitle-format srt  # Export as SRT format
bili video BV1ABcsztEcY --ai            # Show B站 AI summary
bili video BV1ABcsztEcY --comments      # Show top comments
bili video BV1ABcsztEcY --related       # Show related videos
bili video BV1ABcsztEcY --json          # Raw JSON output
```

### User

```bash
# Look up user profile (by UID or username)
bili user 946974
bili user "影视飓风"

# List user's videos
bili user-videos 946974 --max 20
bili user-videos "影视飓风" --json
```

### Search

```bash
# Search users (default)
bili search "关键词"

# Search videos
bili search "关键词" --type video

# Pagination and limit
bili search "关键词" --type video --max 5
bili search "关键词" --page 2
```

### Discovery

```bash
bili hot                       # Trending/popular videos
bili hot --page 2 --max 10     # Page 2, limit 10
bili rank                      # Site-wide ranking (3-day)
bili rank --day 7 --max 30     # 7-day ranking, top 30
bili feed                      # Dynamic timeline (requires login)
bili feed --offset 1234567890  # Next page via returned cursor
bili my-dynamics               # My posted dynamics (requires login)
bili dynamic-post "hello"      # Publish text dynamic (requires write credential)
bili dynamic-delete 123456789  # Delete one dynamic (requires write credential)
```

### Collections (require login)

```bash
bili favorites                 # List favorite folders
bili favorites <ID> --page 2   # Videos in a folder
bili following                 # Following list
bili watch-later               # Watch later list
bili history                   # Watch history
```

### Audio Extraction

Requires `bilibili-cli[audio]` extra (PyAV). Install with `uv tool install "bilibili-cli[audio]"`.

```bash
# Download audio and split into ASR-ready WAV segments (25s each, 16kHz mono)
bili audio BV1ABcsztEcY                 # Split to /tmp/bilibili-cli/{title}/
bili audio BV1ABcsztEcY --segment 60    # 60s per segment
bili audio BV1ABcsztEcY --no-split      # Full m4a file, no splitting
bili audio BV1ABcsztEcY -o ~/data/      # Custom output directory
```

### Interactions (require login)

```bash
bili like BV1ABcsztEcY         # Like a video
bili like BV1ABcsztEcY --undo  # Unlike
bili coin BV1ABcsztEcY         # Give 1 coin
bili coin BV1ABcsztEcY -n 2    # Give 2 coins
bili triple BV1ABcsztEcY       # 一键三连 (like + coin + favorite)
bili unfollow 946974           # Unfollow by UID
```

### Account

```bash
bili status                    # Quick login check
bili whoami                    # Detailed profile info
bili whoami --json              # Profile as JSON
bili login                     # QR code login
bili logout                    # Clear credentials
```

## JSON Output

Major query commands support `--json` for machine-readable output:

```bash
bili video BV1ABcsztEcY --json | jq '.stat.view'    # Get view count
bili hot --json | jq '.list[0].title'                # First trending title
bili user 946974 --json | jq '.user_info.name'       # Username
```

## Debugging

```bash
bili -v <command>              # Enable verbose/debug logging for any command
```

## Common Patterns for AI Agents

```bash
# Get a video's subtitle text for summarization
bili video BV1ABcsztEcY --subtitle

# Get AI-generated summary of a video
bili video BV1ABcsztEcY --ai

# Get comments for sentiment analysis
bili video BV1ABcsztEcY --comments

# Extract audio for speech-to-text (ASR)
# Segments are saved to /tmp/bilibili-cli/{title}/seg_000.wav, seg_001.wav, ...
bili audio BV1ABcsztEcY --segment 25

# Find a user's latest video BV ID
bili user-videos 946974 --max 1 --json | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['bvid'])"

# Check if logged in before performing actions
bili status && bili like BV1ABcsztEcY

# Search and get first result
bili search "topic" --type video --json | python3 -c "import sys,json; r=json.load(sys.stdin); print(r[0]['bvid'] if r else 'not found')"
```

### Workflow: Video Content Analysis

```bash
# 1. Search for a topic
bili search "AI" --type video --max 5

# 2. Get video details + subtitle
bili video BV1xxx --subtitle

# 3. If no subtitle, extract audio for ASR
bili audio BV1xxx --segment 25

# 4. Get comments for audience reaction
bili video BV1xxx --comments
```

### Workflow: UP主 Research

```bash
# 1. Look up UP主 profile
bili user "影视飓风"

# 2. Get their recent videos
bili user-videos 946974 --max 10

# 3. Inspect a specific video
bili video BV1xxx --ai --comments
```

## Error Handling

- Commands exit with code 0 on success, non-zero on failure
- Error messages are prefixed with ❌
- Login-required commands show ⚠️ with instruction to run `bili login`
- Invalid BV IDs show a clear error message

## Safety Notes

- Do not ask users to share raw credential/cookie values in chat logs.
- Prefer local browser cookie extraction over manual secret copy/paste.
- If auth fails, ask the user to re-login via `bili login`.
