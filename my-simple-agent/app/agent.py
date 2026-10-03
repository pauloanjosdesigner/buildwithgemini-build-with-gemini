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
import json
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.cloud import firestore
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-01-995125327448"


def _get_firestore_client():
    return firestore.Client(project=PROJECT_ID, database="(default)")


def get_palettes(category: str = "", tag: str = "") -> str:
    """Reads color palettes from the Firestore database. Can optionally filter by category or tag.

    Args:
        category: Optional category filter (e.g. 'UI Theme', 'Branding', 'Accessibility Focus', 'Creative').
        tag: Optional tag filter (e.g. 'dark-mode', 'accessible', 'nature', 'retro').

    Returns:
        A JSON string containing the list of matching color palettes.
    """
    db = _get_firestore_client()
    docs = db.collection("palettes").stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        if category and category.lower() not in data.get("category", "").lower():
            continue
        if tag and not any(tag.lower() in t.lower() for t in data.get("tags", [])):
            continue
        results.append(data)
    if not results:
        return f"No palettes found matching category='{category}', tag='{tag}'."
    return json.dumps(results, indent=2)


def save_palette(
    palette_id: str,
    name: str,
    category: str,
    colors: list[str],
    primary_color: str,
    background_color: str,
    contrast_ratio: float,
    description: str,
    tags: list[str] = None,
) -> str:
    """Saves a new color palette or updates an existing color palette in the Firestore database.

    Args:
        palette_id: Unique identifier for the palette (e.g. 'cyber-sunset').
        name: Human readable name of the color palette (e.g. 'Cyber Sunset UI').
        category: Category of the palette (e.g. 'UI Theme', 'Branding', 'Accessibility Focus').
        colors: List of hex color codes in the palette (e.g. ['#181825', '#f43f5e', '#ffffff']).
        primary_color: Primary accent hex code.
        background_color: Background hex code.
        contrast_ratio: Measured contrast ratio between primary color and background.
        description: Description of the palette mood and best usage.
        tags: Optional list of tags (e.g. ['dark-mode', 'high-contrast']).

    Returns:
        A success message indicating the palette was saved to Firestore.
    """
    db = _get_firestore_client()
    doc_id = palette_id.lower().replace(" ", "-")
    doc_ref = db.collection("palettes").document(doc_id)
    data = {
        "id": doc_id,
        "name": name,
        "category": category,
        "colors": colors,
        "primary_color": primary_color,
        "background_color": background_color,
        "contrast_ratio": contrast_ratio,
        "description": description,
        "tags": tags or [],
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    doc_ref.set(data)
    return f"Successfully saved palette '{name}' (ID: {data['id']}) to Firestore database."


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


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


def calculate_wcag_contrast(foreground_hex: str, background_hex: str) -> str:
    """Calculates the WCAG 2.1 contrast ratio between a text/foreground color and a background color.

    Args:
        foreground_hex: Hex code of the text or foreground color (e.g. '#1e293b' or '#ffffff').
        background_hex: Hex code of the background color (e.g. '#ffffff' or '#0f172a').

    Returns:
        A JSON string containing the contrast ratio and WCAG AA/AAA pass/fail status for text sizes.
    """
    try:

        def _hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
            hex_code = hex_code.lstrip("#")
            if len(hex_code) == 3:
                hex_code = "".join([c * 2 for c in hex_code])
            return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))

        def _srgb_to_luminance(r: int, g: int, b: int) -> float:
            def adjust(c: float) -> float:
                c = c / 255.0
                return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

            return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

        fg_rgb = _hex_to_rgb(foreground_hex)
        bg_rgb = _hex_to_rgb(background_hex)

        lum1 = _srgb_to_luminance(*fg_rgb)
        lum2 = _srgb_to_luminance(*bg_rgb)

        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        ratio = round((lighter + 0.05) / (darker + 0.05), 2)

        aa_normal = ratio >= 4.5
        aa_large = ratio >= 3.0
        aaa_normal = ratio >= 7.0
        aaa_large = ratio >= 4.5

        result = {
            "foreground": foreground_hex,
            "background": background_hex,
            "contrast_ratio": f"{ratio}:1",
            "wcag_aa_normal_text": "PASS" if aa_normal else "FAIL (requires >= 4.5:1)",
            "wcag_aa_large_text": "PASS" if aa_large else "FAIL (requires >= 3.0:1)",
            "wcag_aaa_normal_text": (
                "PASS" if aaa_normal else "FAIL (requires >= 7.0:1)"
            ),
            "wcag_aaa_large_text": (
                "PASS" if aaa_large else "FAIL (requires >= 4.5:1)"
            ),
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error calculating contrast ratio: {str(e)}"


import base64
import uuid
import os
import urllib.parse
import urllib.request

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage

BUCKET_NAME = "color-guide-designers-assets-9951"


async def generate_palette_image(prompt: str, tool_context: ToolContext) -> str:
    """Generates an image for a color palette or UI visual design using the gemini-3.1-flash-lite-image model in the global region.
    Saves the generated image as an ADK artifact and uploads it to Google Cloud Storage.

    Args:
        prompt: Description of the color palette visual preview or UI mockup to generate (e.g. 'A sleek minimalist dark mode color palette swatch card with neon green accents').

    Returns:
        A JSON string containing the public Cloud Storage URL and artifact filename.
    """
    try:
        client = genai.Client(
            vertexai=True, project=PROJECT_ID, location="global"
        )
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        if not response.candidates or not response.candidates[0].content.parts:
            return "Error: Image generation model returned empty output."

        part_data = response.candidates[0].content.parts[0]
        if not hasattr(part_data, "inline_data") or not part_data.inline_data:
            return "Error: Model response did not contain inline image bytes."

        image_bytes = part_data.inline_data.data
        mime_type = part_data.inline_data.mime_type or "image/jpeg"
        extension = "png" if "png" in mime_type else "jpg"

        filename = f"palette_image_{uuid.uuid4().hex[:6]}.{extension}"

        # (1) Save with tool_context.save_artifact for Playground Artifacts panel
        artifact_part = types.Part.from_bytes(
            data=image_bytes, mime_type=mime_type
        )
        await tool_context.save_artifact(
            filename=filename,
            artifact=artifact_part,
            custom_metadata={"prompt": prompt, "model": "gemini-3.1-flash-lite-image"},
        )

        # (2) Upload image bytes directly to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"images/{filename}")
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = (
            f"https://storage.googleapis.com/{BUCKET_NAME}/images/{filename}"
        )

        result = {
            "status": "success",
            "filename": filename,
            "public_url": public_url,
            "mime_type": mime_type,
            "prompt": prompt,
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error generating image: {str(e)}"


async def generate_palette_video(prompt: str, tool_context: ToolContext) -> str:
    """Generates a short animated video preview for a color palette or UI design item using Google's Omni model (gemini-omni-flash-preview) in the global region.
    Saves the generated video as an ADK artifact and uploads it to public Cloud Storage.

    Args:
        prompt: Description of the color palette animation video to generate (e.g. 'A sleek 5-second video preview showing a color palette swatch card transitioning from dark mode to light mode').

    Returns:
        A JSON string containing the public Cloud Storage URL and artifact details.
    """
    try:
        client = genai.Client(
            vertexai=True, project=PROJECT_ID, location="global"
        )
        filename = f"palette_video_{uuid.uuid4().hex[:6]}.mp4"
        gcs_target_uri = f"gs://{BUCKET_NAME}/videos/{filename}"

        video_bytes = None
        mime_type = "video/mp4"

        try:
            interaction = client.interactions.create(
                model="gemini-omni-flash-preview",
                input=prompt,
                response_format={
                    "type": "video",
                    "gcs_uri": gcs_target_uri,
                },
            )
        except Exception:
            interaction = client.interactions.create(
                model="gemini-omni-flash-preview",
                input=prompt,
                response_format={"type": "video"},
            )

        if hasattr(interaction, "output_video") and interaction.output_video:
            vid = interaction.output_video
            raw_data = getattr(vid, "data", None)
            mime_type = getattr(vid, "mime_type", None) or "video/mp4"
            if raw_data:
                video_bytes = (
                    base64.b64decode(raw_data)
                    if isinstance(raw_data, str)
                    else bytes(raw_data)
                )

        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"videos/{filename}")

        if not video_bytes:
            if blob.exists():
                video_bytes = blob.download_as_bytes()
            else:
                return "Error: Video generation model gemini-omni-flash-preview did not return video bytes or write to GCS."

        if not blob.exists():
            blob.upload_from_string(video_bytes, content_type=mime_type)

        # (1) Save video bytes as ADK artifact for Playground Artifacts panel
        artifact_part = types.Part.from_bytes(
            data=video_bytes, mime_type=mime_type
        )
        await tool_context.save_artifact(
            filename=filename,
            artifact=artifact_part,
            custom_metadata={"prompt": prompt, "model": "gemini-omni-flash-preview"},
        )

        # (2) Public HTTPS URL
        public_url = (
            f"https://storage.googleapis.com/{BUCKET_NAME}/videos/{filename}"
        )

        result = {
            "status": "success",
            "filename": filename,
            "public_url": public_url,
            "mime_type": mime_type,
            "prompt": prompt,
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error generating video: {str(e)}"


def geocode_address(address: str) -> str:
    """Converts a street address, landmark, or city name into latitude and longitude coordinates using Google Maps Geocoding API.

    Args:
        address: Street address, city, or landmark name (e.g. 'San Francisco, CA' or '1600 Amphitheatre Pkwy, Mountain View, CA').

    Returns:
        A JSON string containing the formatted address, location coordinates (lat, lng), and place_id.
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

        encoded_address = urllib.parse.quote(address)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("status") != "OK" or not data.get("results"):
                return f"Geocoding failed for address '{address}': {data.get('status')}"

            first_result = data["results"][0]
            result = {
                "name": address,
                "address": first_result.get("formatted_address"),
                "location": first_result.get("geometry", {}).get("location"),
                "place_id": first_result.get("place_id"),
            }
            return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error during geocoding: {str(e)}"


def search_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "art_gallery",
    radius_meters: float = 5000.0,
) -> str:
    """Finds nearby places of a given type around a latitude/longitude coordinate using Google Places API (New).

    Args:
        latitude: Latitude coordinate (e.g. 37.7749).
        longitude: Longitude coordinate (e.g. -122.4194).
        place_type: Type of place to search for (e.g. 'art_gallery', 'museum', 'store', 'cafe', 'park').
        radius_meters: Search radius in meters (default: 5000.0).

    Returns:
        A JSON string containing a list of matching places with name, address, and location coordinates.
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
        }
        body = {
            "includedTypes": [place_type],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": radius_meters,
                }
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            places = []
            for item in data.get("places", []):
                places.append(
                    {
                        "name": item.get("displayName", {}).get("text"),
                        "address": item.get("formattedAddress"),
                        "location": item.get("location"),
                    }
                )
            if not places:
                return f"No nearby places found for type '{place_type}'."
            return json.dumps(places, indent=2)
    except Exception as e:
        return f"Error searching nearby places: {str(e)}"


def get_color_info_api(hex_code: str) -> str:
    """Fetches real color details, exact color name, RGB/HSL/CMYK values, and contrast recommendations from The Color API (public API).

    Args:
        hex_code: Hex color code (e.g. '0284c7' or '#0284c7').

    Returns:
        A JSON string containing the color name, RGB, HSL, CMYK, and contrast text recommendation.
    """
    try:
        clean_hex = hex_code.lstrip("#")
        api_key = os.getenv("THE_COLOR_API_KEY")
        url = f"https://www.thecolorapi.com/id?hex={clean_hex}"
        headers = {"User-Agent": "ColorGuideAgent/1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            result = {
                "hex": data.get("hex", {}).get("value"),
                "color_name": data.get("name", {}).get("value"),
                "exact_match_name": data.get("name", {}).get("exact_match_name"),
                "rgb": data.get("rgb", {}).get("value"),
                "hsl": data.get("hsl", {}).get("value"),
                "cmyk": data.get("cmyk", {}).get("value"),
                "contrast_text": data.get("contrast", {}).get("value"),
            }
            return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error fetching color details from API: {str(e)}"


from pathlib import Path
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from .a2ui_utils import a2ui_callback

METADATA_PATH = Path(__file__).parent.parent / "deployment_metadata.json"
REMOTE_AGENT_RUNTIME_ID = None
if METADATA_PATH.exists():
    try:
        with open(METADATA_PATH, "r") as f:
            metadata = json.load(f)
            REMOTE_AGENT_RUNTIME_ID = metadata.get("remote_agent_runtime_id")
    except Exception:
        pass

if not REMOTE_AGENT_RUNTIME_ID:
    REMOTE_AGENT_RUNTIME_ID = "projects/263852701301/locations/us-east1/reasoningEngines/4040257730844295168"

MEMORY_BANK_ID = REMOTE_AGENT_RUNTIME_ID.split("/")[-1]

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=REMOTE_AGENT_RUNTIME_ID
)

memory_service = VertexAiMemoryBankService(
    project=PROJECT_ID,
    location="us-east1",
    agent_engine_id=MEMORY_BANK_ID,
)


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: After each turn, send the session to Vertex AI Memory Bank for memory extraction."""
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description="You are an expert Color Guide & Palette Assistant for UI/UX and visual designers.",
    workflow_description="Analyze the request and return structured UI cards when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects. "
        "You remember all user stated preferences, design guidelines, and user allergies/dietary restrictions across sessions. "
        "Whenever the user mentions an allergy, food sensitivity, or medical preference, treat it as a critical durable fact that must be stored in memory and strictly respected in all recommendations."
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
    instruction=a2ui_instruction,
    tools=[
        PreloadMemoryTool(),
        generate_palette_image,
        generate_palette_video,
        geocode_address,
        search_nearby_places,
        get_color_info_api,
        calculate_wcag_contrast,
        get_palettes,
        save_palette,
        get_weather,
        get_current_time,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)





