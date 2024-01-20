import os
import hashlib
from PIL import Image
import cv2

from flask_app.utils.globalUtils import _tempDirectory, _tryListDir, _openJSONDirectoriesFile
from flask_app.utils.displayContent import _hideFilename

def _fixExtension(ext):
    ext_mapping = {'quicktime': 'mov'}

    if ext in ext_mapping:
        return ext_mapping[ext]
    else:
        return ext

# Make directories to store uploaded content
def _makeDirs(fileDir, genre_data):
    if genre_data['separate-content'] == "False":
        os.makedirs(fileDir, exist_ok=True)
    else:
        os.makedirs(f"{fileDir}\\Images", exist_ok=True)
        os.makedirs(f"{fileDir}\\Videos", exist_ok=True)


# Create directory path depending on genre of videos
def _createDirPath(folderName, genre, make_dirs=True):
    genre_data = _openJSONDirectoriesFile()["upload-short-form-genres"][genre]

    fileDir = f"{genre_data['main-dir']}\\{folderName}{genre_data['sub-dir']}"

    if make_dirs:
        _makeDirs(fileDir, genre_data)

    return fileDir


# Rename image using hash
def _generateContentHash(content):
    if content.content_type.split("/")[0] == "video":
        hashable_image = _getFirstFrame(content)
    elif content.content_type.split("/")[0] == "image":
        hashable_image = Image.open(content)
    else:
        raise NameError(f"Unknown Content Type: {content.content_type}")

    return _hash_image(hashable_image)


# Get a frame from a video
def _getVideoFrame(filepath):
    vidcap = cv2.VideoCapture(filepath)
    success, image = vidcap.read()
    if success:
        return Image.fromarray(image)


# Get the first frame of a videofile for hashing purposes
def _getFirstFrame(videofile):
    tempname = f'{_tempDirectory()}\\temp.{videofile.filename.split(".")[-1]}'
    videofile.save(tempname)
    return _getVideoFrame(tempname)

# Handle the naming scheme of both video and image content
def _handleUploadTypeSemantics(content, fileDir, hash_string, separate_content):
    content_type, ext = content.content_type.split("/")

    ext = _fixExtension(ext)

    # Create new filename
    filename = f"{hash_string}.{ext}"

    # Determine whether content is separated into images and videos or all in
    # one directory
    if separate_content == "False":
        existing_content = set(_tryListDir(fileDir))
        endDir = fileDir
    else:
        existing_content = _tryListDir(f"{fileDir}\\Videos")
        existing_content.extend(_tryListDir(f"{fileDir}\\Images"))

        existing_content = set(existing_content)

        # Determine directory of file based on content type
        if content_type == "video":
            endDir = f"{fileDir}\\Videos"
        elif content_type == "image":
            endDir = f"{fileDir}\\Images"
        else:
            raise NameError(f"Unknown Content Type: {content_type}")
    
    # Return 1 if new image uploaded, otherwise return 0
    if filename in existing_content:
        return 0, filename
        
    _uploadImage(content, endDir, filename)
    return 1, filename  


# Hash an image
def _hash_image(image):
    # Convert the image array to bytes and then create an sha256 hash
    return hashlib.sha256(image.tobytes()).hexdigest()


# Upload a single image to the provided directory
# (Create directory if it does not already exist)
def _uploadImage(image, fileDir, filename):
    image.seek(0)

    image.save(f'{fileDir}\\{filename}')


# Upload set of images passed in from POST request
def uploadImageSet(contents, folderName, genre):
    # Generate file directory baed on genre
    fileDir = _createDirPath(folderName, genre)
    separate_content = _openJSONDirectoriesFile()['upload-short-form-genres'][genre]['separate-content']

    # Store count of new uploads
    newUploads = 0
    filenameDict = {}

    # Upload images to server backend
    for content in contents:       
        newUpload, filename = _handleUploadTypeSemantics(content, fileDir, _generateContentHash(content), separate_content)
        
        # Save files in temp folder
        _uploadImage(content, f"{_tempDirectory()}", filename)
        
        newUploads += newUpload
        
        # Add files to dictionary
        filenameDict[_hideFilename(filename)] = {'file': f"{_tempDirectory(True)}/{filename}", 'type': content.content_type.split("/")[0], 
                                  'alt': f'Image from {folderName}', 'duplicate': not newUpload}

    return newUploads, filenameDict
