## Check version
# import tensorflow as tf
# print(tf.__version__)
# print(tf.keras)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dropout

# Image generator
datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train = datagen.flow_from_directory(
    '/Users/wanhoo/Documents/CSE40883/dataset/single_label_pic',
    target_size=(64, 64),
    class_mode='categorical',
    subset='training'
)

val = datagen.flow_from_directory(
    '/Users/wanhoo/Documents/CSE40883/dataset/single_label_pic',
    target_size=(64, 64),
    class_mode='categorical',
    subset='validation'
)


model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
    MaxPooling2D(2, 2),

    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),

    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),

    Flatten(),
    Dense(64, activation='relu'),
    Dropout(0.5), # helps prevent overfitting by making the model less reliant on any one neuron
    Dense(2, activation='softmax')  # 2 output classes
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(train, validation_data=val, epochs=10)

model.save("turn_classifier.h5")


