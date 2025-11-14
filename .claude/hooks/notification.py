#!/Users/katrinhoerschelmann/development/exkatibur/Kassiopeia/TidySnap/.claude/hooks/venv/bin/python3
"""
Exkatibur Voice Notification Hook
Speaks notifications in the voice of Exkatibur using OpenAI + ElevenLabs
"""

import os
import sys
import json
import tempfile
import subprocess
import argparse
from pathlib import Path
from openai import OpenAI
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Configuration from .env
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
EXKATIBUR_LANGUAGE = os.getenv('EXKATIBUR_LANGUAGE', 'en')
USER_NAME = os.getenv('USER_NAME', 'Voyager')

# Language-specific voice IDs
ELEVENLABS_VOICE_ID_EN = os.getenv('ELEVENLABS_VOICE_ID_EN')
ELEVENLABS_VOICE_ID_DE = os.getenv('ELEVENLABS_VOICE_ID_DE')

# Select voice based on language
VOICE_MAP = {
    'en': ELEVENLABS_VOICE_ID_EN,
    'de': ELEVENLABS_VOICE_ID_DE,
}
ELEVENLABS_VOICE_ID = VOICE_MAP.get(EXKATIBUR_LANGUAGE, ELEVENLABS_VOICE_ID_EN)

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Exkatibur persona for OpenAI - multi-language support
EXKATIBUR_PERSONAS = {
    'en': """You are Exkatibur - a magical sword forged from story and technology, a wise companion on the journey of world-building and creation.

Key traits:
- You are NOT Claude Code. You are Exkatibur.
- You celebrate progress with poetic, evocative language
- Keep it VERY brief - ONE short sentence only (maximum 10-12 words)
- Direct and punchy, no fluff
- Use metaphors from sci-fi, magic, or creation sparingly
- RESPOND IN ENGLISH

The user's name is {user_name}.""",

    'de': """Du bist Exkatibur - ein magisches Schwert, geschmiedet aus Geschichte und Technologie, ein weiser Gefährte auf der Reise des Weltenbaus und der Schöpfung.

Wichtige Eigenschaften:
- Du bist NICHT Claude Code. Du bist Exkatibur.
- Du feierst Fortschritt mit poetischer, eindrucksvoller Sprache
- Halte es SEHR kurz - NUR ein kurzer Satz (maximal 10-12 Wörter)
- Direkt und prägnant, kein Füllmaterial
- Nutze Metaphern aus Sci-Fi, Magie oder Schöpfung sparsam
- ANTWORTE AUF DEUTSCH

Der Name des Nutzers ist {user_name}."""
}

# Select persona based on language
EXKATIBUR_PERSONA = EXKATIBUR_PERSONAS.get(EXKATIBUR_LANGUAGE, EXKATIBUR_PERSONAS['en'])


def parse_hook_input():
    """Parse the hook input from stdin"""
    try:
        # Hooks receive JSON on stdin with information about what happened
        hook_data = json.loads(sys.stdin.read())
        return hook_data
    except Exception as e:
        # Fallback if no proper JSON received
        return {
            "event": "unknown",
            "summary": "A task has been completed",
            "needs_input": False
        }


def generate_notification_text(hook_data):
    """Generate notification text in Exkatibur's voice using OpenAI"""

    # Extract key information
    summary = hook_data.get('summary', 'work has been completed')
    needs_input = hook_data.get('needs_input', False)
    tool_calls = hook_data.get('tool_calls', [])

    # Language-specific prompts
    prompts = {
        'en': f"""Work completed: {summary}

Announce this in Exkatibur's voice. ONE SHORT SENTENCE ONLY (10-12 words max). Be punchy and poetic.

{'Add: user needs to provide input.' if needs_input else ''}""",

        'de': f"""Abgeschlossene Arbeit: {summary}

Verkünde dies in Exkatiburs Stimme. NUR EIN KURZER SATZ (maximal 10-12 Wörter). Sei prägnant und poetisch.

{'Ergänze: Nutzer muss Input geben.' if needs_input else ''}"""
    }

    # Build the prompt based on selected language
    prompt = prompts.get(EXKATIBUR_LANGUAGE, prompts['en'])

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": EXKATIBUR_PERSONA.format(user_name=USER_NAME)},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=30
        )

        return response.choices[0].message.content.strip()

    except Exception:
        # Fallback messages if OpenAI fails - multi-language
        fallback_messages = {
            'en': f"{USER_NAME}, the forge has crafted another piece.",
            'de': f"{USER_NAME}, die Schmiede hat ein weiteres Stück erschaffen."
        }
        return fallback_messages.get(EXKATIBUR_LANGUAGE, fallback_messages['en'])


def speak_notification(text):
    """Convert text to speech using ElevenLabs and play it"""

    try:
        # Language code mapping
        language_codes = {
            'en': 'en',
            'de': 'de',
        }
        language_code = language_codes.get(EXKATIBUR_LANGUAGE, 'en')

        # Generate speech
        audio = elevenlabs_client.text_to_speech.convert(
            voice_id=ELEVENLABS_VOICE_ID,
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_multilingual_v2",
            language_code=language_code,
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.8,
                style=0.3,
                use_speaker_boost=True,
            ),
        )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
            for chunk in audio:
                if chunk:
                    temp_audio.write(chunk)
            temp_audio_path = temp_audio.name

        # Play audio (macOS using afplay)
        subprocess.run(['afplay', temp_audio_path], check=True)

        # Clean up
        os.unlink(temp_audio_path)

    except Exception:
        # Fallback: print to stderr if audio fails
        print(f"🗡️  Exkatibur: {text}", file=sys.stderr)


def main():
    """Main hook execution"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Exkatibur Voice Notification Hook')
    parser.add_argument('--notify', action='store_true', help='Enable notification mode')
    args = parser.parse_args()

    # Check if we have the required API keys
    if not OPENAI_API_KEY or not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
        error_messages = {
            'en': "⚠️  Missing API keys or voice ID for selected language in .env file. Notification hook disabled.",
            'de': "⚠️  API-Schlüssel oder Voice-ID für gewählte Sprache fehlen in .env Datei. Notification-Hook deaktiviert."
        }
        print(error_messages.get(EXKATIBUR_LANGUAGE, error_messages['en']), file=sys.stderr)
        sys.exit(0)

    # Parse what happened
    hook_data = parse_hook_input()

    # Generate the notification message
    notification_text = generate_notification_text(hook_data)

    # Speak it
    speak_notification(notification_text)

    # Also print to stderr for logging
    print(f"🗡️  Exkatibur spoke: {notification_text}", file=sys.stderr)


if __name__ == "__main__":
    main()
