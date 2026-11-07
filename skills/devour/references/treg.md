# treg.to fallback

treg is the paid fallback for when yt-dlp is blocked. `scripts/treg_client.py` already holds this logic, so read this only to debug it or to change an endpoint.

Checked against the catalog on 2026-11-07. Prices move, so recheck with `GET https://treg.to/catalog/search?q=...` (no token needed).

| Job | Endpoint id | Method | Params | Price |
|---|---|---|---|---|
| Channel list | `scrapecreators.x.v1-youtube-channel-videos` | GET | `handle` or `channelId`, `sort` (latest, popular), `continuationToken` | $0.00188 |
| Channel list, alternate | `crawl4ai.youtube.channel.videos` | POST | `channel`, `limit` (max 30). Newest first, relative dates, no durations | $0.0009 |
| Transcript | `scrapecreators.x.v1-youtube-video-transcript` | GET | `url`, `language` (a null transcript means that language is missing) | $0.00188 |
| Transcript, alternate | `anyapi.youtube.video_transcript_full` | POST | `url`, `captionKind` (manual, automatic, any), `language` | up to $0.00308 |
| Transcript, alternate | `tikhub.x.youtube-web-v2-get-video-captions` | GET | `video_id` or `video_url`, `language_code`, `format` (srt, xml, json3, txt) | $0.008 |
| Video details | `scrapecreators.youtube.video.detail` | GET | `url`. Not called by the scripts, since videos.json covers it | $0.00188 |

## Token safety

The token comes from the `TREG_TOKEN` environment variable, or else `TREG_API_KEY` in `~/Documents/Projects/.env`, and goes in the `X-Treg-Token` header. treg's `/call/` route also proxies arbitrary tools and URLs and forwards headers to them, so the token must only be sent to the catalog ids above. `treg_client.py` enforces this with an allow-list and refuses redirects, because a redirect would carry the header to another host. Add new endpoints to that list, and don't build `/call/` URLs anywhere else.

## Which account pays

Only that key. The `mcp__treg__*` tools and the `treg` command line are signed in to a separate business account (Splendid Moving), so don't use them for devour, not even for free-looking calls. The catalog search needs no account: use the public `GET https://treg.to/catalog/search?q=...`.
