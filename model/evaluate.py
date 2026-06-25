"""
Landmark Vision — Model Evaluation Script
==========================================
Evaluates the trained model on the validation set and prints a
full classification report + confusion matrix.

Usage:
    python model/evaluate.py
    python model/evaluate.py --data_dir ./data/landmarks --model_path ./model/landmark_model.h5
"""
import os
import argparse
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Evaluate trained landmark model")
parser.add_argument("--data_dir",   default="./data/landmarks")
parser.add_argument("--model_path", default="./model/landmark_model.h5")
parser.add_argument("--img_size",   default=224, type=int)
parser.add_argument("--batch_size", default=32,  type=int)
parser.add_argument("--val_split",  default=0.2, type=float)
args = parser.parse_args()

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

if not os.path.exists(args.model_path):
    logger.error("Model not found: %s — run train.py first.", args.model_path)
    raise SystemExit(1)

logger.info("Loading model from %s", args.model_path)
model = keras.models.load_model(args.model_path)

IMG_SIZE = (args.img_size, args.img_size)

logger.info("Loading validation dataset ...")
val_ds = keras.utils.image_dataset_from_directory(
    args.data_dir,
    validation_split=args.val_split,
    subset="validation",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=args.batch_size,
    shuffle=False,
)

CLASS_NAMES = val_ds.class_names

val_ds_proc = val_ds.map(
    lambda x, y: (preprocess_input(x), y),
    num_parallel_calls=tf.data.AUTOTUNE,
).prefetch(tf.data.AUTOTUNE)

# ── Collect ground truth & predictions ───────────────────────────────────────
logger.info("Running predictions ...")
y_true, y_pred = [], []

for images, labels in val_ds_proc:
    preds  = model.predict(images, verbose=0)
    y_pred.extend(np.argmax(preds, axis=1))
    y_true.extend(labels.numpy())

y_true = np.array(y_true)
y_pred = np.array(y_pred)

# ── Report ────────────────────────────────────────────────────────────────────
acc = np.mean(y_true == y_pred)
logger.info("=" * 60)
logger.info("Overall Accuracy: %.2f%%", acc * 100)
logger.info("=" * 60)

print("\n── Classification Report ──")
print(classification_report(y_true, y_pred, target_names=CLASS_NAMES, digits=3))

# ── Confusion matrix (saved as PNG) ──────────────────────────────────────────
cm = confusion_matrix(y_true, y_pred)
fig, ax = plt.subplots(figsize=(max(10, len(CLASS_NAMES)), max(8, len(CLASS_NAMES) - 2)))
sns.heatmap(
    cm, annot=len(CLASS_NAMES) <= 20,
    fmt="d", cmap="Blues",
    xticklabels=CLASS_NAMES,
    yticklabels=CLASS_NAMES,
    ax=ax,
)
ax.set_title("Confusion Matrix — Landmark Vision", fontsize=14, fontweight="bold")
ax.set_xlabel("Predicted")
ax.set_ylabel("Actual")
plt.tight_layout()

cm_path = os.path.join(os.path.dirname(args.model_path), "confusion_matrix.png")
plt.savefig(cm_path, dpi=150, bbox_inches="tight")
logger.info("Confusion matrix saved → %s", cm_path)
plt.close()
