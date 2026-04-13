# Faceless Engine (Legacy) — Sub-Project Context

**Status:** Legacy / Superseded — kept for reference only
**Active engine:** Use `faceless_engine_google/` instead

## What This Is

The original faceless video pipeline. Uses OpenAI (GPT-4) for scripts, ElevenLabs for voice, and MoviePy for rendering. The pipeline is **fully mocked** — no real API calls are made. It was replaced by `faceless_engine_google/` which uses real Google APIs.

## Key Files

| File | Purpose |
|------|---------|
| `backend/api.py` | FastAPI app on **port 8000** |
| `backend/workers.py` | `VideoPipelineWorker` — mocked pipeline (time.sleep stubs) |

## Pipeline (all mocked)

1. Script generation — GPT-4 placeholder (returns mock text)
2. Voice synthesis — ElevenLabs placeholder (returns mock path)
3. Image generation — placeholder (no images generated)
4. Video compilation — MoviePy placeholder
5. Auto-posting — not implemented

## Do Not

- Do not run or develop this engine — use `faceless_engine_google/` instead
- Do not install dependencies for this engine (OpenAI/ElevenLabs keys not set up)
