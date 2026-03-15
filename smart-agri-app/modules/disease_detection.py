from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

try:
    import tensorflow as tf  # type: ignore
except Exception:  # pragma: no cover
    tf = None

try:
    import torch  # type: ignore
except Exception:  # pragma: no cover
    torch = None


MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
TF_MODEL_PATH = MODEL_DIR / "plant_disease_model.keras"
TORCH_MODEL_PATH = MODEL_DIR / "plant_disease_model.pt"
LABELS_PATH = MODEL_DIR / "plant_disease_labels.json"

TREATMENTS = {
    "Healthy": "No curative treatment required. Maintain balanced irrigation, scouting, and nutrient discipline.",
    "Early Blight": "Use Mancozeb or Chlorothalonil on the recommended label dose and remove lower infected leaves.",
    "Leaf Spot": "Use a copper-based fungicide, improve air movement, and avoid overhead irrigation late in the day.",
    "Nitrogen Deficiency": "Apply split nitrogen dressing, check soil pH, and avoid water stress during recovery.",
    "Powdery Mildew": "Use wettable sulfur or potassium bicarbonate and reduce dense canopy humidity.",
}


@st.cache_resource
def _load_model_bundle():
    labels = ["Healthy", "Early Blight", "Leaf Spot", "Nitrogen Deficiency", "Powdery Mildew"]
    if LABELS_PATH.exists():
        labels = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    if tf is not None and TF_MODEL_PATH.exists():
        return {"framework": "tensorflow", "model": tf.keras.models.load_model(TF_MODEL_PATH), "labels": labels}
    if torch is not None and TORCH_MODEL_PATH.exists():
        model = torch.jit.load(str(TORCH_MODEL_PATH), map_location="cpu")
        model.eval()
        return {"framework": "torch", "model": model, "labels": labels}
    return {"framework": "fallback", "model": None, "labels": labels}


def _fallback_classifier(image: Image.Image) -> tuple[str, float, str]:
    rgb = image.convert("RGB").resize((128, 128))
    arr = np.asarray(rgb).astype(np.float32)
    red = arr[:, :, 0]
    green = arr[:, :, 1]
    brightness = float(arr.mean())
    green_ratio = float((green > red + 8).mean())
    lesion_ratio = float(((red > green + 12) & (brightness < 135)).mean())
    pale_ratio = float(((brightness > 155) & (green < 150)).mean())

    if green_ratio > 0.48 and lesion_ratio < 0.06:
        return "Healthy", 0.93, "Strong green canopy ratio with limited lesion-like pixels."
    if lesion_ratio > 0.18:
        return "Early Blight", 0.88, "High brown-red lesion density with darker stressed tissue."
    if pale_ratio > 0.22:
        return "Nitrogen Deficiency", 0.84, "Leaf surface appears pale with reduced healthy green intensity."
    if lesion_ratio > 0.1:
        return "Leaf Spot", 0.82, "Discrete dark regions suggest localized spotting pressure."
    return "Powdery Mildew", 0.78, "Diffuse surface discoloration suggests fungal surface stress."


def detect_plant_disease(image: Image.Image) -> dict:
    bundle = _load_model_bundle()
    framework = bundle["framework"]

    if framework == "tensorflow":
        tensor = np.asarray(image.convert("RGB").resize((224, 224))).astype("float32") / 255.0
        pred = bundle["model"].predict(np.expand_dims(tensor, axis=0), verbose=0)[0]
        index = int(np.argmax(pred))
        disease_name = bundle["labels"][index]
        probability = float(pred[index])
        reasoning = "TensorFlow classifier evaluated disease patterns from the uploaded plant sample."
    elif framework == "torch":
        arr = np.asarray(image.convert("RGB").resize((224, 224))).astype("float32") / 255.0
        tensor = torch.tensor(arr.transpose(2, 0, 1)).unsqueeze(0)  # type: ignore[arg-type]
        with torch.no_grad():  # type: ignore[union-attr]
            pred = bundle["model"](tensor)[0]
            prob = torch.softmax(pred, dim=0)  # type: ignore[union-attr]
            index = int(torch.argmax(prob).item())  # type: ignore[union-attr]
            disease_name = bundle["labels"][index]
            probability = float(prob[index].item())
        reasoning = "PyTorch classifier evaluated disease patterns from the uploaded plant sample."
    else:
        disease_name, probability, reasoning = _fallback_classifier(image)

    return {
        "disease_name": disease_name,
        "probability": round(probability * 100, 1),
        "recommended_treatment": TREATMENTS.get(disease_name, "Inspect the sample physically and consult a local extension worker."),
        "reasoning": reasoning,
        "model_source": framework,
    }
