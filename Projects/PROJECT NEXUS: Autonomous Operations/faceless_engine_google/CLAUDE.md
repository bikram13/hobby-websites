# Faceless Engine Google — Sub-Project Context

**Status:** Active
**Port:** 8001 | **Stack:** Gemini 2.5 Pro + Google Cloud TTS + Imagen 3 + MoviePy

## What This Is

The active faceless video pipeline powered entirely by Google APIs. Generates AI scripts, synthesizes voice, creates scene images, compiles video, and auto-posts to YouTube and Instagram.

## Key Files

| File | Purpose |
|------|---------|
| `backend/api_google.py` | FastAPI app on **port 8001**, serves frontend at `/`, outputs at `/outputs` |
| `backend/workers_google.py` | `GoogleVideoPipelineWorker` — full 5-step pipeline |
| `backend/trend_engine.py` | `TrendEngine` — Gemini selects viral topic from seeded trend list |
| `backend/poster.py` | `YouTubePoster`, `InstagramPoster`, `LinkedInPoster` (stub), `post_to_socials()` |

## Pipeline (5 steps)

1. **Script** — Gemini 2.5 Pro (`models/gemini-2.5-pro`), 45-second narration
2. **Voice** — Google Cloud TTS, `en-US-Neural2-D` (Neural2 male), MP3 output
3. **Images** — Imagen 3 (`imagen-3.0-generate-001`), 5 scenes at 9:16 vertical
4. **Captions** — Gemini 1.5 Flash transcribes audio → word-level timestamps JSON
5. **Video** — MoviePy: ImageClip array + AudioFileClip → 24fps MP4 (libx264/aac)

Auto-post: `post_to_socials()` runs after compile — uploads to YouTube Shorts + Instagram Reels.

## Autonomous Mode

Set topic = `"AUTO"` (or leave blank) → `TrendEngine.get_viral_topic()` selects topic + tone via Gemini 1.5 Flash from a seeded trend list. Returns `{topic, tone, hook}`.

## Required Env Vars (.env)

```
GOOGLE_AI_API_KEY        # Gemini + Imagen 3 (Google AI Studio)
GOOGLE_APPLICATION_CREDENTIALS  # Path to service account JSON (Cloud TTS)
INSTAGRAM_ACCESS_TOKEN   # Meta Graph API token
INSTAGRAM_BUSINESS_ID    # Instagram Business Account ID
INSTAGRAM_APP_ID         # Meta App ID
```
YouTube auth uses OAuth: `client_secrets.json` + `youtube_token.json` (gitignored).

## Commands

```bash
cd backend
pip install -r ../requirements.txt
uvicorn api_google:app --port 8001 --reload

# Test trend engine standalone
python trend_engine.py
```

## Fallback Behavior

- If `google-generativeai` not installed → script returns mock text, images skipped
- If `google-cloud-texttospeech` not installed → voice skipped, audio path returned as placeholder
- If Imagen 3 quota exceeded → PIL placeholder images (dark gradient, "AI AGENT MODE" text)
- If MoviePy compilation fails → exception propagates, job marked failed in DB

## Output Files

Generated to `outputs/` (gitignored):
- `{job_id}_voice.mp3`
- `{job_id}_scene_0..4.png`
- `{job_id}_final.mp4`

## Do Not

- Do not commit `client_secrets.json` or `youtube_token.json` (gitignored, OAuth credentials)
- Do not commit files in `outputs/` or `assets/` (gitignored, large binaries)
- LinkedIn posting is a stub — `LinkedInPoster.upload_video()` prints placeholder and returns None
