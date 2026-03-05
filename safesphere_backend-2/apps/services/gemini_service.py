"""
GeminiService – generates structured FIR drafts using Google Gemini API.

Model used : gemini-1.5-flash  (fast + free tier available)
Setup      : pip install google-generativeai
             Add GEMINI_API_KEY to your .env
             Get key at: https://aistudio.google.com/app/apikey
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


# ── FIR Prompt Template ───────────────────────────────────────────────────────
# This exact prompt is sent to Gemini to produce the formatted FIR document.

FIR_PROMPT = """
You are a legal assistant helping generate a structured FIR (First Information Report) based on emergency incident evidence.

Use the following inputs extracted from an emergency safety system:

User Details:
Name: {user_name}

Incident Location:
Latitude: {latitude}
Longitude: {longitude}
Address (if available): {location_text}

Time of Incident:
{timestamp}

Audio Transcript from Recording:
{audio_transcript}

Video Observation Summary:
{video_description}

Emergency Trigger Source:
User activated safety trigger and evidence was automatically recorded.

Your task is to generate a **formal FIR draft** suitable for submission to a police station.

Requirements:
1. Write in formal legal tone.
2. Clearly describe the incident based on the evidence.
3. Mention the time, location, and context.
4. Include that digital evidence (audio/video) has been recorded and stored.
5. Avoid assumptions if information is unclear.
6. Structure the FIR in proper sections.

FIR FORMAT:

Police Station: [Nearest Station if known, otherwise write "To be determined based on jurisdiction"]

Complainant Details:
Name: {user_name}

Date & Time of Incident:
{timestamp}

Location of Incident:
{location_text}

Incident Description:
(Use transcript and video description to explain what happened)

Evidence Available:
- Video Recording
- Audio Recording
- GPS Location Data
- Timestamped Digital Evidence

Declaration:
This report is generated from an emergency safety system where the user activated a distress trigger and the system automatically recorded evidence.

Return the FIR as a clear formatted document.
""".strip()


class GeminiService:
    """
    Calls the Google Gemini API to generate a formal FIR document
    from emergency case data.

    Quick start:
        1. pip install google-generativeai
        2. Set GEMINI_API_KEY=your-key in .env
        3. Call GeminiService().generate_fir(...)
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY

        if not self.api_key:
            logger.warning(
                "⚠️  GEMINI_API_KEY is not set in .env — "
                "FIR generation will fail until you add it.\n"
                "Get a free key at: https://aistudio.google.com/app/apikey"
            )

    # ── Main public method ────────────────────────────────────────────────────

    def generate_fir(
        self,
        user_name: str,
        latitude: str,
        longitude: str,
        timestamp: str,
        audio_transcript: str = "No audio transcript available.",
        video_description: str = "No video description available.",
        location_text: str = None,
    ) -> str:
        """
        Sends case details to Gemini and returns the generated FIR text.

        Args:
            user_name         : Full name of the user who triggered the SOS
            latitude          : GPS latitude string
            longitude         : GPS longitude string
            timestamp         : ISO8601 datetime string of the incident
            audio_transcript  : Transcribed text from audio evidence (optional)
            video_description : Summary of video evidence (optional)
            location_text     : Human-readable address – auto-built from GPS if not given

        Returns:
            Formatted FIR document as a plain-text string
        """
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing from .env\n"
                "Get your free key at: https://aistudio.google.com/app/apikey"
            )

        # Build a readable location string if address not provided
        if not location_text:
            location_text = f"GPS Coordinates – Latitude: {latitude}, Longitude: {longitude}"

        # Fill in the prompt template with real case data
        filled_prompt = FIR_PROMPT.format(
            user_name=user_name,
            latitude=latitude,
            longitude=longitude,
            location_text=location_text,
            timestamp=timestamp,
            audio_transcript=audio_transcript,
            video_description=video_description,
        )

        # ── Call Gemini API ───────────────────────────────────────────────────
        try:
            import google.generativeai as genai
        except ImportError:
            raise RuntimeError(
                "google-generativeai package is not installed.\n"
                "Run: pip install google-generativeai"
            )

        genai.configure(api_key=self.api_key)

        # gemini-1.5-flash: fast, free-tier available, ideal for hackathons
        model = genai.GenerativeModel("gemini-1.5-flash")

        logger.info(f"[GeminiService] Generating FIR for user: {user_name}")

        response = model.generate_content(
            filled_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,         # Low → consistent formal output
                max_output_tokens=2048,
            ),
        )

        fir_text = response.text
        logger.info(f"[GeminiService] FIR generated successfully ({len(fir_text)} chars)")
        return fir_text
