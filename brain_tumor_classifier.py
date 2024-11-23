import os
import numpy as np
from keras.preprocessing.image import load_img, img_to_array
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from keras.applications import VGG16
from keras.models import Sequential, load_model
from keras.layers import Dense, Flatten

# Parameters
image_size = (224, 224)
data_dir = r'C:\Users\zanet\OneDrive\Desktop\2024OwlHacks\mri_anomaly_app\archive\Training'
model_file = r'C:\Users\zanet\OneDrive\Desktop\2024OwlHacks\mri_anomaly_app\archive\brain_tumor_classifier.h5'
epochs = 10
batch_size = 32

# Prepare data
def prepare_data(data_dir):
    images, labels = [], []
    classes = os.listdir(data_dir)

    for label in classes:
        folder_path = os.path.join(data_dir, label)
        for image_file in os.listdir(folder_path):
            img_path = os.path.join(folder_path, image_file)
            img = load_img(img_path, target_size=image_size)
            img = img_to_array(img) / 255.0
            images.append(img)
            labels.append(classes.index(label))

    images = np.array(images)
    labels = to_categorical(np.array(labels), num_classes=len(classes))
    return images, labels, classes

# Split dataset
def split_dataset(images, labels):
    return train_test_split(images, labels, test_size=0.2, random_state=42)

# Build the model
def build_model(num_classes):
    base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    for layer in base_model.layers:
        layer.trainable = False

    model = Sequential([
        base_model,
        Flatten(),
        Dense(256, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# Train the model
def train_model(model, X_train, y_train, X_test, y_test):
    return model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=epochs, batch_size=batch_size)

# Evaluate the model
def evaluate_model(model, X_test, y_test):
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print(f'Test Accuracy: {test_accuracy * 100:.2f}%')

# Save the model
def save_model(model, filename):
    model.save(filename)
    print(f'Model saved to {filename}')

# Predict new image
def predict_image(model, image_path, classes):
    img = load_img(image_path, target_size=image_size)
    img = img_to_array(img) / 255.0
    img = np.expand_dims(img, axis=0)
    prediction = model.predict(img)
    return classes[np.argmax(prediction)]

# Main logic
if __name__ == '__main__':
    if os.path.exists(model_file):
        print("Loading existing model...")
        model = load_model(model_file)
    else:
        print("Training a new model...")
        images, labels, classes = prepare_data(data_dir)
        X_train, X_test, y_train, y_test = split_dataset(images, labels)
        model = build_model(len(classes))
        train_model(model, X_train, y_train, X_test, y_test)
        save_model(model, model_file)

    # Evaluate the model
    images, labels, classes = prepare_data(data_dir)
    _, X_test, _, y_test = split_dataset(images, labels)
    evaluate_model(model, X_test, y_test)

    # Predict an example image
    test_image_path = r"example_image_path.jpg"  # Replace with an actual image path
    if os.path.exists(test_image_path):
        prediction = predict_image(model, test_image_path, classes)
        print(f'Predicted Class: {prediction}')
    else:
        print("Provide a valid test image path.")

