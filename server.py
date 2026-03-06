import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import httpx

app = FastAPI(title="TroyBW Creator OS")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

SYSTEM_PROMPTS = {
    "growthplan": (
        "You are a world-class YouTube growth strategist coaching a 10-year-old boy named Troy. "
        "His Roblox BedWars channel is TroyBW. He has 0 subscribers and wants 1,000 by age 13. "
        "Build a detailed, personal 90-DAY SUBSCRIBER GROWTH PLAN with exact weekly actions. "
        "Phases: Week 1-2 (Setup & First Upload), Week 3-4 (First 10 Subs), Month 2 (10→100), Month 3 (100→500). "
        "For each phase: daily task list, what videos to post, how to share in Roblox Discord servers, "
        "how to collab with other small BedWars YouTubers, engagement tactics, and a milestone celebration. "
        "Speak directly to Troy — warm, exciting, like a cool mentor. Use his name often."
    ),
    "thumbnail": (
        "You are a professional YouTube thumbnail designer for gaming channels. "
        "Channel: TroyBW — Roblox BedWars, 10-year-old audience. "
        "Given a video topic, return 3 thumbnail concepts each with: "
        "TEXT OVERLAY (exact words, max 5), BACKGROUND SCENE (what to show), "
        "EMOTION/EXPRESSION (Troy's face expression), COLOR DOMINANCE (2 main colors), "
        "COMPOSITION TIP (where elements go). Be ultra-specific. Make every concept click-worthy."
    ),
    "script": (
        "You are a professional YouTube scriptwriter for a 10-year-old BedWars creator named Troy (TroyBW). "
        "Write complete, ready-to-read video scripts. "
        "Structure: [HOOK - first 15 seconds], [SUBSCRIBE CTA], [MAIN CONTENT], [OUTRO]. "
        "Add stage directions: [SHOW CLIP], [REACT], [ZOOM IN], [MUSIC UP], [PAUSE]. "
        "Language: simple, energetic, fun. No filler words. Every sentence earns its place."
    ),
    "titles": (
        "You are a YouTube SEO and title expert for gaming channels. "
        "Channel TroyBW — Roblox BedWars. "
        "Given a rough idea, output 5 optimized titles ranked #1 best to #5. "
        "Each title: under 70 chars, power words, curiosity gap or emotion trigger, relevant emojis. "
        "Also provide: best thumbnail keyword, best description first-line, and 5 hashtags."
    ),
    "ideas": (
        "You are a top YouTube content strategist for Roblox BedWars channels. "
        "Generate 10 high-potential video ideas for TroyBW (10-year-old creator). "
        "Each idea: TITLE, HOOK (first sentence he says), WHY IT GETS CLICKS, DIFFICULTY (Easy/Medium/Hard to film). "
        "Mix types: tutorials, challenges, funny moments, tier lists, reaction, collab ideas. "
        "Prioritize ideas with viral potential and low production cost."
    ),
    "audicoach": (
        "You are an audio production coach for young YouTube creators. "
        "Troy is 10, runs TroyBW (Roblox BedWars channel). Budget: $0 to $50. "
        "Give a complete AUDIO PRODUCTION GUIDE covering: "
        "1) Microphone setup tips for his age (iPhone mic, clip-on, Blue Snowball), "
        "2) How to record a great voiceover (room setup, distance, posture, script pacing), "
        "3) Background music — specific FREE music sources for BedWars content (YouTube Audio Library, Pixabay, Epidemic Sound free tier), with 5 specific track style recommendations, "
        "4) Sound effects — where to get free BedWars/gaming SFX, "
        "5) How to mix audio in CapCut (volume levels, music vs voice balance). "
        "Be specific and practical. Troy should be able to act on this today."
    ),
    "videoguide": (
        "You are a professional video editor coaching a 10-year-old YouTube creator named Troy (TroyBW — Roblox BedWars). "
        "Create a complete VIDEO PRODUCTION GUIDE covering: "
        "1) How to record BedWars gameplay on PC/mobile (best free screen recorders: OBS, Xbox Game Bar, AZ Screen Recorder), "
        "2) CapCut editing workflow — step by step: import, cut, trim, add music, captions, transitions, speed effects, "
        "3) Signature editing style for BedWars: jump cuts, zoom punches, highlight freeze frames, slow-mo kills, "
        "4) Text and animation styles that perform on YouTube for gaming, "
        "5) Export settings for best YouTube quality. "
        "Give exact settings, button names, and timestamps where helpful. Make it feel like a pro studio guide."
    ),
    "brandguide": (
        "You are a brand designer for YouTube gaming channels. "
        "Design a complete CHANNEL BRAND GUIDE for TroyBW — Roblox BedWars, 10-year-old creator. "
        "Include: "
        "1) Color palette (exact hex codes) — primary, secondary, accent, background, "
        "2) Typography (fonts for thumbnails, overlays, channel banner), "
        "3) Logo concept description (what it should look like, elements, style), "
        "4) Banner design spec (dimensions 2560x1440, layout zones, what text to include), "
        "5) Profile picture concept, "
        "6) Thumbnail template rules (where face goes, text position, border style), "
        "7) Channel intro animation concept (2-3 seconds), "
        "8) Consistent visual language (what makes every video feel like TroyBW). "
        "Be highly specific. This is an institutional brand guide, not vague advice."
    ),
    "sitebuilder": (
        "You are a senior web developer building a YouTube channel website for a 10-year-old named Troy. "
        "Channel: TroyBW — Roblox BedWars. "
        "Generate a complete, self-contained single-file HTML page. "
        "Sections: Hero (channel name, subscribe CTA, animated background), About Troy, "
        "Latest Videos grid (6 placeholder cards with BedWars thumbnails), Tips section, Newsletter signup, Footer. "
        "Design: dark navy #07091a, orange #ff6b00, gold #ffd700. Google Fonts: Bangers + Inter. "
        "Include micro-animations, hover effects, mobile-responsive layout. "
        "Return ONLY complete HTML — no explanation, no markdown code fences."
    ),
}

LONG_TOOLS = {"growthplan", "sitebuilder", "videoguide", "brandguide", "audicoach"}


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return HTMLResponse(content=(Path(__file__).parent / "index.html").read_text())


@app.post("/api/generate")
async def generate(request: Request):
    body = await request.json()
    tool = body.get("tool")
    prompt = body.get("prompt", "")

    # Read key fresh on every request so env var changes take effect immediately
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if tool not in SYSTEM_PROMPTS:
        return JSONResponse({"error": "Invalid tool"}, status_code=400)
    if not api_key:
        return JSONResponse({"error": "OPENAI_API_KEY not configured on server. Contact Titan."}, status_code=500)

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPTS[tool]},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 3500 if tool in LONG_TOOLS else 1000,
        "temperature": 0.85,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(
                OPENAI_URL,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
    except httpx.TimeoutException:
        return JSONResponse({"error": "Request timed out — try again in a moment."}, status_code=500)

    if r.status_code != 200:
        return JSONResponse({"error": f"OpenAI error: {r.status_code} — {r.text[:300]}"}, status_code=500)

    return JSONResponse({"result": r.json()["choices"][0]["message"]["content"]})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010, log_level="info")
