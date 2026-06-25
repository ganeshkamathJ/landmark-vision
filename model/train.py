"""
Landmark Vision — MobileNetV2 Fine-Tuning Script
================================================
Dataset: vaslemon/pictures-of-famous-places (~53 MB)
         kaggle datasets download -d vaslemon/pictures-of-famous-places -p ./data/
         Unzip to: ./data/landmarks/<class_name>/<image.jpg>

Usage:
    python model/train.py
    python model/train.py --data_dir ./data/landmarks --epochs 20 --batch_size 32
"""

import os
import sys
import argparse
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# ── CLI args ──────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Train MobileNetV2 landmark classifier")
parser.add_argument("--data_dir",   default="./data/landmarks", help="Path to dataset root (one subfolder per class)")
parser.add_argument("--model_dir",  default="./model",          help="Directory to save trained model")
parser.add_argument("--img_size",   default=224, type=int,      help="Input image size (square)")
parser.add_argument("--batch_size", default=32,  type=int)
parser.add_argument("--epochs_head",default=10,  type=int,      help="Epochs for phase 1 (head only)")
parser.add_argument("--epochs_fine",default=10,  type=int,      help="Epochs for phase 2 (fine-tuning)")
parser.add_argument("--val_split",  default=0.2, type=float)
parser.add_argument("--fine_tune_layers", default=30, type=int, help="Number of top base layers to unfreeze in phase 2")
args = parser.parse_args()

# ── Validate data directory ───────────────────────────────────────────────────
if not os.path.isdir(args.data_dir):
    logger.error("Dataset directory not found: %s", args.data_dir)
    logger.error("Please download the dataset first:")
    logger.error("  kaggle datasets download -d vaslemon/pictures-of-famous-places -p ./data/")
    logger.error("  Expand and place images in ./data/landmarks/<class_name>/<images>")
    sys.exit(1)

os.makedirs(args.model_dir, exist_ok=True)

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

logger.info("TensorFlow version: %s", tf.__version__)
logger.info("GPUs available: %s", tf.config.list_physical_devices('GPU'))

IMG_SIZE    = (args.img_size, args.img_size)
BATCH_SIZE  = args.batch_size
AUTOTUNE    = tf.data.AUTOTUNE
MODEL_PATH  = os.path.join(args.model_dir, "landmark_model.h5")
LABELS_PATH = os.path.join(args.model_dir, "landmark_labels.txt")

# ── Load dataset ──────────────────────────────────────────────────────────────
logger.info("Loading dataset from: %s", args.data_dir)

train_ds = keras.utils.image_dataset_from_directory(
    args.data_dir,
    validation_split=args.val_split,
    subset="training",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
)

val_ds = keras.utils.image_dataset_from_directory(
    args.data_dir,
    validation_split=args.val_split,
    subset="validation",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
)

CLASS_NAMES = train_ds.class_names
NUM_CLASSES = len(CLASS_NAMES)
logger.info("Found %d classes: %s", NUM_CLASSES, CLASS_NAMES[:5])

# Save class labels
with open(LABELS_PATH, "w") as f:
    f.write("\n".join(CLASS_NAMES))
logger.info("Class labels saved to %s", LABELS_PATH)

# ── Preprocessing & Augmentation ─────────────────────────────────────────────
data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
    layers.RandomBrightness(0.1),
    layers.RandomContrast(0.1),
], name="data_augmentation")

def prepare(ds, augment=False):
    ds = ds.map(lambda x, y: (preprocess_input(x), y), num_parallel_calls=AUTOTUNE)
    if augment:
        ds = ds.map(lambda x, y: (data_augmentation(x, training=True), y), num_parallel_calls=AUTOTUNE)
    return ds.cache().prefetch(buffer_size=AUTOTUNE)

train_ds = prepare(train_ds, augment=True)
val_ds   = prepare(val_ds,   augment=False)

# ── Build model ───────────────────────────────────────────────────────────────
logger.info("Building MobileNetV2 model ...")

base_model = MobileNetV2(
    input_shape=(*IMG_SIZE, 3),
    include_top=False,
    weights="imagenet",
)
base_model.trainable = False   # Phase 1: freeze base

inputs = keras.Input(shape=(*IMG_SIZE, 3))
x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(256, activation="relu")(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(NUM_CLASSES, activation="softmax")(x)

model = keras.Model(inputs, outputs, name="LandmarkVision")
model.summary(print_fn=logger.info)

# ── Phase 1: Train classification head ───────────────────────────────────────
logger.info("=" * 60)
logger.info("Phase 1: Training classification head (%d epochs)", args.epochs_head)
logger.info("=" * 60)

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

callbacks = [
    keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True, verbose=1),
    keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3, verbose=1),
    keras.callbacks.ModelCheckpoint(MODEL_PATH, save_best_only=True, verbose=1),
]

history1 = model.fit(
    train_ds,
    epochs=args.epochs_head,
    validation_data=val_ds,
    callbacks=callbacks,
    verbose=1,
)

# ── Phase 2: Fine-tune top layers ─────────────────────────────────────────────
logger.info("=" * 60)
logger.info("Phase 2: Fine-tuning top %d base layers (%d epochs)", args.fine_tune_layers, args.epochs_fine)
logger.info("=" * 60)

base_model.trainable = True
for layer in base_model.layers[:-args.fine_tune_layers]:
    layer.trainable = False

logger.info("Trainable layers: %d / %d", sum(l.trainable for l in model.layers), len(model.layers))

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-5),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

history2 = model.fit(
    train_ds,
    epochs=args.epochs_fine,
    validation_data=val_ds,
    callbacks=callbacks,
    verbose=1,
)

# ── Final save & report ───────────────────────────────────────────────────────
model.save(MODEL_PATH)
logger.info("Model saved → %s", MODEL_PATH)

val_loss, val_acc = model.evaluate(val_ds, verbose=0)
logger.info("Final validation accuracy: %.2f%%", val_acc * 100)
logger.info("Final validation loss:     %.4f",   val_loss)

# Save training summary
summary = {
    "num_classes":    NUM_CLASSES,
    "class_names":    CLASS_NAMES,
    "image_size":     args.img_size,
    "val_accuracy":   round(val_acc * 100, 2),
    "val_loss":       round(val_loss, 4),
    "epochs_phase1":  args.epochs_head,
    "epochs_phase2":  args.epochs_fine,
}

summary_path = os.path.join(args.model_dir, "training_summary.json")
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)

logger.info("Training summary saved → %s", summary_path)
logger.info("Done! Run the app with: python run.py")
