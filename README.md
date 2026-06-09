# 🎬 Video Editing Agent

An AI-powered video editing agent that processes natural language requests and applies video edits automatically using fal.ai models.

---

## ✨ Features

| Feature | Description |
|---|---|
|  Style Transfer | Transform video into anime, cinematic, watercolor, etc. |
|  Video Outpainting | Expand frame beyond original aspect ratio |
|  Lip Sync | Sync character lips to a new audio track |
| ⬆ Upscaling | Enhance video resolution up to 4K |
| ⏱ Extend Duration | Generate new frames to lengthen the video |
|  Object Swap | Replace objects, persons, or backgrounds with an image |
|  Background Removal | Remove or isolate video background |
|  Kling AI | Advanced tier — handles complex multi-edit requests |

---

## 🗂️ Project Structure

```
VideoEditingAgents/
├── api/                        # FastAPI backend
│   ├── main.py                 # App entry point, CORS, health check
│   ├── routers/
│   │   ├── upload.py           # File upload endpoints
│   │   └── chat.py             # Chat/session endpoints
│   ├── services/
│   │   ├── file_service.py     # Cloudinary upload + validation
│   │   ├── session_service.py  # In-memory session store
│   │   └── pipeline_service.py # Orchestrates the full pipeline
│   └── models/
│       ├── requests.py         # Pydantic request models
│       └── responses.py        # Pydantic response models
│
├── graph/                      # LangGraph pipeline
│   ├── graph_builder.py        # Builds the agent graph
│   ├── nodes.py                # All graph nodes
│   └── edges.py                # Conditional routing logic
│
├── routing_agent/              # Decomposes prompt → features + tier
│   ├── agent.py
│   ├── features.py             # Feature registry
│   ├── prompts.py
│   └── schemas.py
│
├── planning_agent/             # Builds execution plan + cost estimate
│   ├── agent.py
│   ├── pricing.py              # Cost calculation per feature
│   ├── execution_order.py      # Feature execution ordering
│   ├── prompts.py
│   └── schemas.py
│
├── agents/                     # Feature parameter collection agents
│   ├── base_agent.py
│   ├── style_transfer_agent.py
│   ├── upscaling_agent.py
│   ├── lip_sync_agent.py
│   ├── extend_duration_agent.py
│   ├── object_agent.py
│   ├── background_agent.py
│   ├── outpainting_agent.py
│   └── kling_agent.py
│
├── execution_agent/            # Runs fal.ai models sequentially
│   ├── agent.py
│   ├── schemas.py
│   └── runners/                # One runner per feature
│       ├── base_runner.py
│       ├── style_transfer_runner.py
│       ├── upscaling_runner.py
│       └── ...
│
├── state/
│   └── shared_state.py         # SharedState TypedDict
│
├── ui/                         # Streamlit frontend
│   ├── app.py                  # Entry point
│   ├── api_client.py           # HTTP calls to FastAPI
│   ├── pages/
│   │   ├── upload_page.py
│   │   ├── chat_page.py
│   │   └── result_page.py
│   └── components/
│       ├── file_uploader.py
│       ├── chat_bubble.py
│       ├── plan_card.py
│       └── video_player.py
│
├── pyproject.toml
├── .env                        # API keys (not committed)
└── README.md
```

---

## ⚙️ How It Works

```
User uploads files (video, images, audio)
            ↓
User types editing request in natural language
            ↓
Routing Agent → decomposes prompt into atomic edits → picks tier (Basic/Kling)
            ↓
Planning Agent → builds ordered execution plan → calculates cost per step
            ↓
User confirms or rejects the plan
            ↓
Feature Agents → collect missing parameters via conversation
            ↓
Execution Agent → runs fal.ai models sequentially (output of each → input of next)
            ↓
Final edited video URL returned to user
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- [ffmpeg](https://ffmpeg.org/download.html) installed and in PATH
- API keys for: OpenAI, fal.ai, Cloudinary

### 1 — Clone the repository

```bash
git clone https://github.com/your-username/VideoEditingAgents.git
cd VideoEditingAgents
```

### 2 — Install dependencies

```bash
uv sync
```

### 3 — Set up environment variables

Create a `.env` file in the root directory:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# fal.ai — for running AI video models
FAL_KEY=key-...

# Cloudinary — for file storage
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

**Where to get the keys:**
- OpenAI: https://platform.openai.com/api-keys
- fal.ai: https://fal.ai/dashboard/keys
- Cloudinary: https://cloudinary.com/users/register_free → Dashboard

### 4 — Run the FastAPI backend

```bash
uv run uvicorn api.main:app --reload --port 8000
```

Verify it's running:
```
http://localhost:8000/health
http://localhost:8000/docs
```

### 5 — Run the Streamlit UI (new terminal)

```bash

uv run streamlit run ui/app.py
```

Open in browser:
```
http://localhost:8501
```

---

## 📡 API Endpoints

### Upload

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload/video` | Upload video (MP4, MOV — max 200MB) |
| POST | `/upload/image` | Upload single image (JPG, PNG, WEBP — max 10MB) |
| POST | `/upload/images` | Upload up to 4 images at once |
| POST | `/upload/audio` | Upload audio (MP3, WAV, OGG, M4A, AAC — max 50MB) |

### Chat

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat/start` | Start new editing session |
| POST | `/chat/message` | Send follow-up message |
| POST | `/chat/confirm` | Confirm or reject the plan |

### Health

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API status and keys |

---

## 🧪 Test Cases

### Test 1 — Single feature (Style Transfer)

```
Upload: Style Transfer.mp4
Prompt: "Beautiful modern anime film style, night scene. A man with glasses and a blue jacket inside a bus at night. Warm interior bus lighting, glowing neon city lights blurred outside the window, crisp line art, cozy and moody atmosphere."

Expected:
- Routing Agent → ["style_transfer"] → basic tier
- Plan shows 1 step with cost 
- After confirm → style_transfer runner executes
(0.10 per output video second in style transfer)0.10 * 5 (Duration) =0.5
```

---

### Test 2 — Multiple features (Basic tier)

```
Upload: Style_Transfer_Upscaling.MP4 
Prompt: "make it a monochromatic pencil sketch with cross-hatching for shading upscale it to 4K
"

Expected:
- Routing Agent → ["style_transfer", "upscaling"] → basic tier
- Plan shows 2 steps with individual costs + total
-After confirm →style_transfer runner executes
- Execution: style_transfer output → upscaling input (chaining)
-
Step 1 — Style Transfer

0.10 × 5.041667s = 0.5042

Step 2 — Video Upscaling

 ($0.001 per megapixel (width × height × frames)) 
 0.001 × (1248×704×151 frames) / 1M = 0.1329
Total: $0.6371
```

---

### Test 3 — Advanced tier (Kling)

```
Upload: Advance_Teir.video + cat.jpg
Prompt:"Swap the dog in this video with the cat from @Element1, then outpaint the canvas from the top, with more sky and clouds extending above."



Expected:
- Routing Agent → kling (cheaper for 2+ features)
- Plan shows 1 step (Kling handles everything)
-After confirm
- elements: [{"image_url": "..."}] in final params
- Prompt does NOT contain the image URL

$0.168 per video duration second
0.168 × 5.007007s = 0.8412
```

---

### Test 4 — Lip Sync

```
Upload: lipsync.mp4 + lipsync.wav (@Audio1)
Prompt: "Sync the person's lips to the audio from @Audio1"

Expected:
- Routing Agent → ["lip_sync"] → basic tier
-After confirm
- Feature agent collects audio_url from @Audio1
- lip_sync runner executes with video_url + audio_url

Step 1 — Lip Sync
Synchronize character lip movements to audio track

$1.3302

(8.00 per minute for Lip sync) 8.00/min × (duration of audio )9.976633s = 1.3302
```








---

### Test 7 — File upload validation

```
Try uploading:
- A .txt file as video → expect 400: "Unsupported video format"
- A video larger than 200MB → expect 400: "Video size exceeds maximum"
- More than 4 images at once → expect 400: "Maximum 4 images allowed"
```

---

### Test 8 — Health check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "cloudinary": "set",
  "openai_key": "set"
}
```

---

## 💰 Pricing Reference

| Feature | Pricing |
|---|---|
| Style Transfer | $0.10 per output second |
| Outpainting | $0.08 per video second |
| Lip Sync | $8.00 per minute |
| Upscaling | $0.001 per megapixel |
| Extend Duration | $0.10 per added second |
| Object Swap | $0.40 (≤5s) / $0.80 (>5s) |
| Background Removal | $0.00111 per compute second |
| Kling AI | $0.168 per video second |

> The system automatically picks Basic or Kling tier based on which is cheaper for your request.

---

## ⚠️ Known Limitations

- Sessions are stored **in-memory** — lost on server restart. Use Redis in production.
- Running multiple uvicorn workers will break sessions (each worker has its own memory).
- Video metadata (duration, dimensions) is not updated between execution steps — cost estimates are based on original video.
- fal.ai requires a paid balance to run AI models.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + uvicorn |
| AI Pipeline | LangGraph |
| LLM | OpenAI GPT-4o-mini |
| Video Models | fal.ai |
| File Storage | Cloudinary |
| Frontend | Streamlit |
| Validation | Pydantic v2 |
