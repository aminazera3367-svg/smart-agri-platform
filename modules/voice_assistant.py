from __future__ import annotations

import tempfile

try:
    import speech_recognition as sr  # type: ignore
except Exception:  # pragma: no cover
    sr = None


def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    if sr is None:
        return "Voice support dependency is not installed. Use the text prompt fallback."
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
        temp_file.write(audio_bytes)
        temp_file.flush()
        with sr.AudioFile(temp_file.name) as source:
            audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except Exception:
            return "Could not transcribe the uploaded audio clearly."


def answer_farmer_question(question: str) -> str:
    q = question.lower()
    if "which crop" in q and "season" in q:
        return "Use the crop planner and location panel together. The strongest choice should balance soil fit, water availability, mandi trend, and current demand pressure."
    if "price" in q or "market" in q:
        return "Check the Price Forecasting page. It combines mandi history, weather pressure, and demand index before estimating the next selling range."
    if "fertilizer" in q or "nitrogen" in q:
        return "Use the AI Agronomist simulator to review nitrogen stress and fertilizer dose before applying a blanket schedule."
    return "Use the planner for crop choice, the forecast page for price timing, and the agronomist page for soil and plant health guidance."
