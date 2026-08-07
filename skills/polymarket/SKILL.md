---
name: polymarket
description: Use this skill when the user is building anything related to Polymarket — fetching market data, placing orders, reading positions, analyzing trades, writing bots, scripts, or any other Polymarket integration. Trigger whenever the user mentions Polymarket, prediction markets, CLOB orders, or wants to interact with Polymarket's API.
---

# Polymarket Development

## Library

Always use the official Polymarket Python SDK located at `/home/nikita/py-sdk`.

Install it into any project with:
```bash
pip install /home/nikita/py-sdk
# or with uv:
uv add /home/nikita/py-sdk
```

Import from the `polymarket` package:
```python
from polymarket import PublicClient, SecureClient
```

## Client types

**PublicClient** — read-only, no credentials needed. Use for fetching markets, prices, order books, trade history:
```python
with PublicClient() as client:
    market = client.get_market(url="https://polymarket.com/event/...")
```

**SecureClient** — requires a private key and API keys. Use for placing/cancelling orders, reading account positions:
```python
with SecureClient(...) as client:
    client.place_order(...)
```

Both have async variants: `AsyncPublicClient`, `AsyncSecureClient`.
