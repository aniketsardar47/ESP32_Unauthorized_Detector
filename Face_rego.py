import os
import face_recognition
import dlib
import numpy as np
from PIL import Image
def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
            img_path = os.path.join(folder, filename)
            image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image)
            for encoding in encodings:
                images.append((encoding, filename, image))
    return images

# Function to save unauthorized faces
def save_unauthorized_faces(image, unauthorized_folder, filename):
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) > 0:
        for i, face_location in enumerate(face_locations):
            top, right, bottom, left = face_location
            unauthorized_face = image[top:bottom, left:right]
            pil_image = Image.fromarray(unauthorized_face)
            pil_image.save(os.path.join(unauthorized_folder, f"{filename[:-4]}_{i}.jpg"))

# Function to check if the input image matches any of the authorized faces
def check_authorization(input_folder, authorized_folder, unauthorized_folder):
    # Load images and encodings from authorized folder
    authorized_faces = load_images_from_folder(authorized_folder)

    # Initialize a set to store the filenames of unauthorized faces already saved
    saved_unauthorized_faces = set()

    # Load the HOG face detector from dlib
    hog_face_detector = dlib.get_frontal_face_detector()

    # Process all images from the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
            input_image_path = os.path.join(input_folder, filename)
            # Load the input image
            input_image = face_recognition.load_image_file(input_image_path)

            # Detect faces in the input image using dlib
            dlib_faces = hog_face_detector(input_image)

            # Convert the dlib rectangles to (top, right, bottom, left) format used by face_recognition
            face_locations = [(face.top(), face.right(), face.bottom(), face.left()) for face in dlib_faces]

            # Check if any faces were detected
            if len(face_locations) > 0:
                # Encode faces in the input image
                input_encodings = face_recognition.face_encodings(input_image, known_face_locations=face_locations)

                # Compare the input image encodings with authorized faces
                for input_encoding in input_encodings:
                    authorized = False
                    for auth_encoding, auth_filename, auth_image in authorized_faces:
                        match = face_recognition.compare_faces([auth_encoding], input_encoding)
                        if match[0]:
                            print(f"The person in the input image {filename} is authorized: {auth_filename}")
                            authorized = True
                            break
                    if not authorized:
                        # Check if the unauthorized face has already been saved
                        if filename not in saved_unauthorized_faces:
                            save_unauthorized_faces(input_image, unauthorized_folder, filename)
                            saved_unauthorized_faces.add(filename)

    if not saved_unauthorized_faces:
        print("All persons in the input images are authorized.")

# Example usage:
input_folder = "E:/AI Jarvis using python tut/Features/inner/"
authorized_folder = r"E:\AI Jarvis using python tut\Features\authorize"  
unauthorized_folder = r"E:\AI Jarvis using python tut\Features\unauthorize"
check_authorization(input_folder, authorized_folder, unauthorized_folder)
