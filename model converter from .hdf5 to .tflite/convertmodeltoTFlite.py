import tensorflow as tf
from tensorflow.keras.models import load_model

# Load the original Keras model
model = load_model("fer2013_mini_XCEPTION.102-0.66.hdf5", compile=False)

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# (Optional) Quantization for smaller size + faster inference
# converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()

# Save TFLite model
with open("emotion_model.tflite", "wb") as f:
    f.write(tflite_model)

print("✅ Model converted to TFLite!")

