import asyncio
from app.routes.format_route import format_transcription, FormatRequest
async def main():
    req = FormatRequest(transcription="Hola", model_name="gemma4:latest")
    resp = await format_transcription(req)
    if hasattr(resp, "body_iterator"):
        async for chunk in resp.body_iterator:
            print(chunk)
asyncio.run(main())
