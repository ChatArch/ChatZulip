# test_chatzulip_basic

Doc-first real-service smoke plan for `chatzulip`. These commands require a valid ChatEnv `zulip` profile and should be run manually or in an integration environment with safe credentials.

## Environment

- `ZULIP_SITE`
- `ZULIP_BOT_EMAIL`
- `ZULIP_BOT_API_KEY`

## Cases

```bash
chatenv test -t zulip -I
chatzulip profile
chatzulip streams
chatzulip topics --stream general
chatzulip search-topics conjecture --all-streams --limit 20
chatzulip search comparator --stream lean4 --since-hours 168 --limit 20
chatzulip messages --stream general --before 5
chatzulip topic --stream general --topic announcements --output /tmp/chatzulip-topic.md
chatzulip news --stream general --since-hours 24 --output /tmp/chatzulip-news.md
```

## Acceptance

- Commands return non-sensitive summaries only.
- Generated Markdown files contain no credential values.
- If optional `chatzulip[llm]` is unavailable, `news` may fall back to a rule-based summary and still succeed.
