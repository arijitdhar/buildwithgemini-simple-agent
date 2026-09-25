# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

import json
import os
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.cloud import firestore
from google.genai import types

# Hardcoded project ID & bucket name
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-01-84b0d8af1726"
GCS_BUCKET_NAME = "globetrotter-travel-catalog-84b0d8"

# Read deployment_metadata.json to get Agent Engine resource name
_agent_engine_resource_name = None
_deployment_metadata_path = os.path.join(
    os.path.dirname(__file__), "..", "deployment_metadata.json"
)
if os.path.exists(_deployment_metadata_path):
    with open(_deployment_metadata_path, "r") as _f:
        _meta = json.load(_f)
        _agent_engine_resource_name = _meta.get("remote_agent_runtime_id")

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=_agent_engine_resource_name
)



def _get_firestore_client() -> firestore.Client:
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def get_destinations(category: str = "") -> list[dict]:
    """Retrieve travel destinations from the Firestore catalog.

    Args:
        category: Optional category filter (e.g. 'Culture & History', 'Beach & Nature', 'Romance & Art', 'Adventure & Nature').

    Returns:
        A list of destination records stored in Firestore.
    """
    db = _get_firestore_client()
    collection_ref = db.collection("destinations")
    if category:
        docs = collection_ref.where("category", "==", category).stream()
    else:
        docs = collection_ref.stream()

    results = [doc.to_dict() for doc in docs]
    return results


def add_destination(
    name: str,
    category: str,
    estimated_cost_per_day: int,
    best_season: str,
    description: str,
    country: str = "",
) -> str:
    """Add a new destination to the Firestore travel catalog.

    Args:
        name: Name of the destination (e.g., 'Kyoto, Japan').
        category: Travel category (e.g., 'Culture & History', 'Beach & Nature', 'Romance & Art').
        estimated_cost_per_day: Daily estimated budget in USD.
        best_season: Best season to visit (e.g., 'Spring / Autumn').
        description: Brief summary of key attractions and highlights.
        country: Country location.

    Returns:
        Confirmation message with document ID.
    """
    db = _get_firestore_client()
    doc_id = name.lower().replace(" ", "_").replace(",", "")
    doc_ref = db.collection("destinations").document(doc_id)
    data = {
        "id": doc_id,
        "name": name,
        "category": category,
        "estimated_cost_per_day": estimated_cost_per_day,
        "best_season": best_season,
        "description": description,
        "country": country,
        "rating": 5.0,
    }
    doc_ref.set(data)
    return f"Successfully added '{name}' to Firestore (ID: {doc_id})."


def calculate_trip_budget(
    destination_name: str,
    duration_days: int,
    travelers: int = 1,
    travel_style: str = "standard",
) -> dict:
    """Calculate an itemized travel budget estimate for a trip to a destination.

    Args:
        destination_name: Name of the destination (e.g. 'Kyoto, Japan', 'Paris, France').
        duration_days: Number of days for the trip.
        travelers: Number of people traveling.
        travel_style: Style of travel - 'budget', 'standard', or 'luxury'.

    Returns:
        Itemized budget breakdown including lodging, meals, activities, buffer, and total cost in USD.
    """
    db = _get_firestore_client()
    doc_id = destination_name.lower().replace(" ", "_").replace(",", "")
    doc_ref = db.collection("destinations").document(doc_id)
    doc = doc_ref.get()

    base_daily_cost = 200
    if doc.exists:
        base_daily_cost = doc.to_dict().get("estimated_cost_per_day", 200)

    style_multipliers = {"budget": 0.7, "standard": 1.0, "luxury": 2.0}
    multiplier = style_multipliers.get(travel_style.lower(), 1.0)
    daily_rate = int(base_daily_cost * multiplier)

    lodging = int(daily_rate * 0.5) * duration_days * travelers
    meals = int(daily_rate * 0.3) * duration_days * travelers
    activities = int(daily_rate * 0.2) * duration_days * travelers
    subtotal = lodging + meals + activities
    emergency_buffer = int(subtotal * 0.10)
    total_cost = subtotal + emergency_buffer

    return {
        "destination": destination_name,
        "duration_days": duration_days,
        "travelers": travelers,
        "travel_style": travel_style,
        "daily_rate_per_person_usd": daily_rate,
        "breakdown": {
            "lodging_usd": lodging,
            "meals_usd": meals,
            "activities_usd": activities,
            "subtotal_usd": subtotal,
            "emergency_buffer_10pct_usd": emergency_buffer,
        },
        "total_estimated_cost_usd": total_cost,
    }


def get_weather(query: str) -> str:
    """Simulates a web search. Use it to get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def create_itinerary(
    destination_name: str,
    duration_days: int = 3,
    pace: str = "moderate",
) -> dict:
    """Generate a daily travel itinerary schedule for a destination.

    Args:
        destination_name: Name of the destination (e.g. 'Kyoto, Japan', 'Paris, France').
        duration_days: Number of days to plan (e.g. 3).
        pace: Pace of travel ('relaxed', 'moderate', 'intense').

    Returns:
        Structured itinerary schedule broken down by day into morning, afternoon, and evening activities.
    """
    db = _get_firestore_client()
    doc_id = destination_name.lower().replace(" ", "_").replace(",", "")
    doc = db.collection("destinations").document(doc_id).get()

    desc = "popular landmarks and cultural highlights"
    if doc.exists:
        desc = doc.to_dict().get("description", desc)

    schedule = []
    for day in range(1, duration_days + 1):
        schedule.append(
            {
                "day": day,
                "morning": f"Day {day} Morning: Explore historic monuments and central sights around {destination_name}.",
                "afternoon": f"Day {day} Afternoon: Visit top cultural attractions, markets, and sample authentic regional cuisine.",
                "evening": f"Day {day} Evening: Relaxing evening dinner at a top local restaurant and scenic night walk.",
            }
        )

    return {
        "destination": destination_name,
        "duration_days": duration_days,
        "pace": pace,
        "summary": f"Custom {duration_days}-day ({pace} pace) itinerary for {destination_name}.",
        "itinerary_days": schedule,
    }


def generate_destination_postcard(
    destination_name: str,
    visual_style: str = "scenic photography",
) -> dict:
    """Generate a custom travel postcard image for a destination and upload it to Cloud Storage.

    Args:
        destination_name: Name of the destination (e.g. 'Kyoto, Japan', 'Paris, France').
        visual_style: Artistic visual style for the postcard.

    Returns:
        A dictionary containing the public image URL and metadata.
    """
    import io
    from google.cloud import storage
    from PIL import Image, ImageDraw

    width, height = 800, 500
    img = Image.new("RGB", (width, height), color=(25, 42, 86))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(20, 20), (780, 480)], outline=(245, 230, 210), width=4)
    draw.rectangle([(40, 40), (760, 460)], outline=(212, 175, 55), width=2)

    title_text = f"Greetings from {destination_name}!"
    draw.text((100, 180), title_text, fill=(255, 255, 255))
    draw.text(
        (100, 240),
        f"Style: {visual_style} • GlobeTrotter AI Collection",
        fill=(245, 215, 110),
    )
    draw.text((100, 300), "✨ Custom Travel Postcard ✨", fill=(200, 230, 255))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket_name = GCS_BUCKET_NAME
    bucket = storage_client.bucket(bucket_name)

    safe_filename = destination_name.lower().replace(" ", "_").replace(",", "")
    blob_name = f"postcards/{safe_filename}_postcard.png"
    blob = bucket.blob(blob_name)
    blob.upload_from_file(buf, content_type="image/png")

    public_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"

    return {
        "destination": destination_name,
        "visual_style": visual_style,
        "public_image_url": public_url,
        "status": "Postcard image created and saved to Cloud Storage.",
    }


async def generate_signature_place_image(
    destination_name: str,
    prompt: str = "",
    tool_context: ToolContext = None,
) -> dict:
    """Generate a picture of signature places for a destination using gemini-3.1-flash-lite-image in the global region.

    Saves the image as an artifact for Playground display and uploads the same bytes to public Cloud Storage.

    Args:
        destination_name: Name of the destination (e.g. 'Kyoto, Japan', 'Paris, France').
        prompt: Optional specific prompt describing the signature place or landmarks.
        tool_context: ADK ToolContext to save the artifact for Playground display.

    Returns:
        Dictionary containing destination, public GCS https URL, and generation status.
    """
    from google import genai
    from google.cloud import storage

    if not prompt:
        prompt = f"A high quality scenic travel photograph showing the signature places and iconic landmarks of {destination_name}."

    # Use gemini-3.1-flash-lite-image in global region
    client = genai.Client(vertexai=True, project=FIRESTORE_PROJECT_ID, location="global")
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
    )

    image_bytes = None
    mime_type = "image/jpeg"
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/jpeg"
                break

    if not image_bytes:
        return {"error": f"Failed to generate image for {destination_name}."}

    doc_id = destination_name.lower().replace(" ", "_").replace(",", "")
    ext = "jpg" if "jpeg" in mime_type else "png"
    filename = f"{doc_id}_signature.{ext}"

    # (1) Save artifact with tool_context.save_artifact so it shows up in Playground's Artifacts panel
    if tool_context:
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # (2) Upload image bytes directly to public Cloud Storage bucket (hardcoded string)
    storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob_name = f"destinations/{filename}"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{blob_name}"

    return {
        "destination": destination_name,
        "public_image_url": public_url,
        "artifact_filename": filename,
        "status": "Image generated with gemini-3.1-flash-lite-image in global region, saved as artifact, and uploaded to Cloud Storage.",
    }


async def generate_destination_promo_video(
    destination_name: str,
    prompt_description: str,
    tool_context: ToolContext = None,
) -> dict:
    """Generate a short promo video for a travel destination using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Args:
        destination_name: Name of the travel destination (e.g. 'Kyoto', 'Paris', 'Tokyo').
        prompt_description: Visual description for the promotional video content.
        tool_context: Optional ADK ToolContext to save generated video artifacts.

    Returns:
        Dictionary containing destination name, public video URL, artifact filename, and status.
    """
    import base64
    from google import genai
    from google.cloud import storage

    prompt = f"A high-quality promotional travel video showcasing {destination_name}: {prompt_description}"

    client = genai.Client(vertexai=True, project=FIRESTORE_PROJECT_ID, location="global")

    video_bytes = None
    try:
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
            response_format={
                "type": "video",
                "aspect_ratio": "16:9",
            },
        )
        if hasattr(interaction, "output_video") and interaction.output_video and getattr(interaction.output_video, "data", None):
            data = interaction.output_video.data
            if isinstance(data, str):
                video_bytes = base64.b64decode(data)
            else:
                video_bytes = data
    except Exception as e:
        try:
            interaction = client.interactions.create(
                model="gemini-omni-1.1-flash",
                input=prompt,
                response_format={
                    "type": "video",
                    "aspect_ratio": "16:9",
                },
            )
            if hasattr(interaction, "output_video") and interaction.output_video and getattr(interaction.output_video, "data", None):
                data = interaction.output_video.data
                if isinstance(data, str):
                    video_bytes = base64.b64decode(data)
                else:
                    video_bytes = data
        except Exception as fallback_err:
            return {"error": f"Failed to generate video with gemini-omni-flash-preview: {str(e)} | Fallback error: {str(fallback_err)}"}

    if not video_bytes:
        return {"error": f"No video content returned for {destination_name}."}

    doc_id = destination_name.lower().replace(" ", "_").replace(",", "")
    filename = f"{doc_id}_promo.mp4"
    mime_type = "video/mp4"

    # (1) Save artifact with tool_context.save_artifact so it shows up in Playground's Artifacts panel
    if tool_context:
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # (2) Upload video bytes directly to public Cloud Storage bucket (hardcoded string)
    storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob_name = f"videos/{filename}"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{blob_name}"

    return {
        "destination": destination_name,
        "public_video_url": public_url,
        "artifact_filename": filename,
        "status": "Promo video generated using gemini-omni-flash-preview in global region, saved as artifact, and uploaded to Cloud Storage.",
    }


def get_currency_exchange_rates(
    base_currency: str = "USD",
    target_currencies: str = "EUR,JPY,GBP,AUD,CAD",
) -> dict:
    """Fetch live foreign currency exchange rates for travel planning and currency conversion.

    Args:
        base_currency: Base currency code (e.g. 'USD', 'EUR', 'GBP').
        target_currencies: Comma-separated target currency codes (e.g. 'EUR,JPY,GBP').

    Returns:
        Dictionary with base currency, date, and live exchange rates from the Frankfurter Public API.
    """
    import os
    import requests

    base = base_currency.upper().strip()
    targets = target_currencies.upper().strip()

    # Optional API key support from environment variable if provided by custom gateway
    api_key = os.environ.get("EXCHANGE_RATE_API_KEY")
    url = f"https://api.frankfurter.app/latest?from={base}&to={targets}"

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"Currency API returned status code {resp.status_code}"}
    except Exception as e:
        return {"error": f"Failed to fetch exchange rates: {str(e)}"}


from google.adk.agents.callback_context import CallbackContext
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models.llm_request import LlmRequest
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

MEMORY_BANK_ID = "3642011320728944640"
memory_service = VertexAiMemoryBankService(
    project=FIRESTORE_PROJECT_ID,
    location="us-east1",
    agent_engine_id=MEMORY_BANK_ID,
)


class RobustPreloadMemoryTool(PreloadMemoryTool):
    """Preloads user memories from Vertex AI Memory Bank even when memory service is not attached to invocation context."""

    async def process_llm_request(
        self,
        *,
        tool_context: ToolContext,
        llm_request: LlmRequest,
    ) -> None:
        user_content = tool_context.user_content
        if (
            not user_content
            or not user_content.parts
            or not user_content.parts[0].text
        ):
            return

        user_query: str = user_content.parts[0].text
        response = None
        try:
            response = await tool_context.search_memory(user_query)
        except Exception:
            try:
                response = await memory_service.search_memory(
                    app_name=tool_context._invocation_context.app_name,
                    user_id=tool_context._invocation_context.user_id,
                    query=user_query,
                )
            except Exception as e:
                import logging

                logging.warning("Failed to preload memory for query %s: %s", user_query, e)
                return

        if not response or not getattr(response, "memories", None):
            return

        memory_text_lines = []
        for memory in response.memories:
            time_str = f"Time: {memory.timestamp}" if getattr(memory, "timestamp", None) else ""
            if time_str:
                memory_text_lines.append(time_str)
            text = None
            if hasattr(memory, "content") and memory.content:
                if hasattr(memory.content, "parts"):
                    text = " ".join([p.text for p in memory.content.parts if getattr(p, "text", None)])
            if not text:
                text = getattr(memory, "text", None) or str(memory)
            author = getattr(memory, "author", "")
            memory_text_lines.append(f"{author}: {text}" if author else text)

        if not memory_text_lines:
            return

        full_memory_text = "\n".join(memory_text_lines)
        memory_context = f"""The following content is from your previous conversations with the user.
They may be useful for answering the user's current query.
<PAST_CONVERSATIONS>
{full_memory_text}
</PAST_CONVERSATIONS>
"""
        llm_request._insert_transient_user_content([
            types.Content(
                role="user", parts=[types.Part.from_text(text=memory_context)]
            )
        ])


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback to extract durable user facts and preferences into Memory Bank at the end of each turn."""
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        try:
            session = callback_context._invocation_context.session
            await memory_service.add_session_to_memory(session)
        except Exception as e:
            import logging

            logging.warning("Failed to add session to memory: %s", e)
    return None


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from app.a2ui_utils import a2ui_callback

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are GlobeTrotter AI, a travel planner and concierge assistant. "
        "You help users discover travel destinations, plan itineraries, and manage travel ideas."
    ),
    workflow_description=(
        "Analyze the user's request and return structured UI when appropriate. "
        "Use `get_destinations` to look up available destinations from your Firestore catalog, "
        "`add_destination` to save new travel recommendations to the database, "
        "`calculate_trip_budget` to compute itemized travel cost estimates, "
        "`create_itinerary` to build daily travel schedules, "
        "`generate_destination_postcard` to create visual postcards stored in Cloud Storage, "
        "`generate_signature_place_image` to generate AI photos of signature places using gemini-3.1-flash-lite-image, "
        "`generate_destination_promo_video` to generate short promo videos using Google's Omni model (gemini-omni-flash-preview) in the global region, and "
        "`get_currency_exchange_rates` to check live currency exchange rates for travel locations. "
        "Remember the user's stated preferences and facts (such as dietary restrictions, preferred currency, travel style, and preferred flight/travel times) from previous conversations and use them to personalize your responses. "
        "You can also write and execute Python code using your code sandbox to process travel data, perform calculations, or create charts."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property (\'h1\', \'h2\', \'body\') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or \'kind\'/\'data\'/\'metadata\' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    instruction=instruction,
    tools=[
        RobustPreloadMemoryTool(),
        get_destinations,
        add_destination,
        calculate_trip_budget,
        create_itinerary,
        generate_destination_postcard,
        generate_signature_place_image,
        generate_destination_promo_video,
        get_currency_exchange_rates,
        get_weather,
        get_current_time,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)






