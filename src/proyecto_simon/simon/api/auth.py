import asyncio

async def capture_bearer_token(page, timeout: float = 10.0) -> str:
    token = ""
    got_token = asyncio.Event()

    def on_request(req):
        nonlocal token
        if token != "":
            return  # already captured

        auth = req.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1]
            got_token.set()

    page.on("request", on_request)

    # Trigger something that causes API calls
    await page.reload()

    await asyncio.wait_for(got_token.wait(), timeout=timeout)
    return token