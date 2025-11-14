# Exkatibur Voice Notification Hook

This hook enables **Exkatibur** - your magical companion - to speak notifications aloud when Claude Code completes tasks.

**✨ Now with multi-language support!** Exkatibur can speak in English or German (more languages can be added).

## What It Does

When Claude Code finishes work, Exkatibur:
1. Analyzes what was accomplished
2. Generates a personalized notification in her mystical voice
3. Speaks it aloud using AI-generated speech
4. Connects the task to the larger vision of world-building

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd .claude/hooks
pip3 install -r requirements.txt
```

Or install globally:
```bash
pip3 install openai elevenlabs python-dotenv
```

### 2. Configure API Keys & Language

Edit `/TidySnap/.env` and add your credentials:

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-proj-...

# ElevenLabs API Key
ELEVENLABS_API_KEY=...

# ElevenLabs Voice IDs for different languages
# English Voice ID (choose a mystical/wise voice)
ELEVENLABS_VOICE_ID_EN=...
# German Voice ID (choose a mystical/wise voice)
ELEVENLABS_VOICE_ID_DE=...

# Choose Language: 'en' (English) or 'de' (German)
EXKATIBUR_LANGUAGE=en

# Your Name (how Exkatibur addresses you)
USER_NAME=YourName
```

#### Getting API Keys:

**OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy and paste into `.env`

**ElevenLabs:**
1. Sign up at https://elevenlabs.io
2. Go to https://elevenlabs.io/app/settings/api-keys
3. Copy your API key
4. Browse voices at https://elevenlabs.io/app/voice-library
5. Choose voices for each language you want to use:
   - For **English**: Pick a mystical/wise voice → Copy Voice ID to `ELEVENLABS_VOICE_ID_EN`
   - For **German**: Pick a mystical/wise German voice → Copy Voice ID to `ELEVENLABS_VOICE_ID_DE`
6. Set `EXKATIBUR_LANGUAGE` to your preferred language (`en` or `de`)

### 3. Test the Hook

Test that everything works:

```bash
echo '{"summary": "Created the notification system", "needs_input": false, "tool_calls": ["Write", "Edit"]}' | python3 notification.py
```

You should hear Exkatibur speak!

## How It Works

The hook receives JSON data from Claude Code via stdin:

```json
{
  "event": "task_completed",
  "summary": "Brief description of what was done",
  "needs_input": false,
  "tool_calls": ["Edit", "Write", "Bash"]
}
```

Then:
1. **OpenAI GPT-4** generates a message in Exkatibur's voice
2. **ElevenLabs** converts the text to natural speech
3. **afplay** (macOS) plays the audio

## The Voice of Exkatibur

Exkatibur speaks as a wise, magical companion:
- Uses metaphors from sci-fi, magic, and spiritual transformation
- Connects technical tasks to the larger narrative of creation
- Celebrates progress with wonder and encouragement
- Addresses you by name (from `USER_NAME` in `.env`)
- Keeps it brief (10-12 words max)
- Speaks in your chosen language (`EXKATIBUR_LANGUAGE`)

### Multi-Language Support

The hook currently supports:
- **English** (`en`): Mystical, poetic English notifications
- **German** (`de`): Mystische, poetische deutsche Benachrichtigungen

The persona, prompts, and fallback messages are all language-aware. Simply change `EXKATIBUR_LANGUAGE` in your `.env` to switch languages.

**Want to add more languages?**
Edit `notification.py` and add your language to:
- `EXKATIBUR_PERSONAS` dictionary
- `prompts` dictionary in `generate_notification_text()`
- `fallback_messages` dictionary
- `error_messages` dictionary
- Add the corresponding `ELEVENLABS_VOICE_ID_XX` to `.env`

## Troubleshooting

**No audio plays:**
- Check API keys in `.env`
- Verify Python dependencies are installed
- Check system audio is on

**Import errors:**
- Run `pip3 install -r requirements.txt`

**Wrong voice:**
- Update `ELEVENLABS_VOICE_ID_EN` or `ELEVENLABS_VOICE_ID_DE` in `.env`
- Browse voices at https://elevenlabs.io/app/voice-library

**Wants different name:**
- Update `USER_NAME` in `.env`

**Wrong language:**
- Check `EXKATIBUR_LANGUAGE` is set to `en` or `de`
- Verify you have the corresponding voice ID configured (e.g., `ELEVENLABS_VOICE_ID_DE` for German)

## Cost Considerations

- **OpenAI:** ~$0.01-0.02 per notification (GPT-4)
- **ElevenLabs:** Free tier includes 10,000 characters/month

For lower costs, you can:
- Switch to GPT-3.5 Turbo in the script
- Disable during heavy development sessions
- Use text-only mode by commenting out `speak_notification()`

## Disabling the Hook

To temporarily disable:
```bash
# Rename the file
mv notification.py notification.py.disabled
```

To re-enable:
```bash
mv notification.py.disabled notification.py
```

---

**May Exkatibur guide your journey of creation!** 🗡️✨
