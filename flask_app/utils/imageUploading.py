import os
import hashlib
from PIL import Image
import cv2

from flask_app.utils.globalUtils import _tempDirectory, _tryListDir
from flask_app.utils.database import database

db = database()


def _retreiveMemeCaptions(contentPath, content_hash, img_ext):
    returnedCaptions = []
    existingCaptions = set()

    try:
        # Try opening caption file for current image if it exists
        with open(f"{contentPath}\\Captions\\{content_hash}_{img_ext}.txt", "r") as captionFile:
            # Loop through all the captions that already exist in file and store one as 
            # set and one in a return list
            for line in captionFile:
                line = line.strip()
                returnedCaptions.append("\n\n".join(line.split("***")))
                existingCaptions.add(line)
    except FileNotFoundError:
        pass
    
    return returnedCaptions, existingCaptions


def _handleCaptionUpload(contentPath, content_hash, caption, img_ext):
    if not caption:
        return [], 0, ""
    
    returnedCaptions, existingCaptions = _retreiveMemeCaptions(contentPath, content_hash, img_ext)
    duplicate = True

    # Write caption to file
    with open(f"{contentPath}\\Captions\\{content_hash}_{img_ext}.txt", "a") as captionFile:
        # Replace delimiter string with general delimiter
        caption = caption.replace('\r\n', '***').replace('\n', '***').replace('•••', '***')

        # Only write captions if they do not exist yet
        if caption not in existingCaptions:
            captionFile.write(f"{caption}\n")
            returnedCaptions.append("\n\n".join(caption.split("***")))
            duplicate = False

    return returnedCaptions, duplicate, f"{contentPath}\\Captions\\{content_hash}_{img_ext}.txt"


def _createDirectoryPath(dir_info, source_name, captions):
    if dir_info['search_dir_storage']:
        contentPath = f"{dir_info['section_directory']}"
    else:
        contentPath = f"{dir_info['section_directory']}\\{source_name}"

    if dir_info['separate_uploaded_content']:
        contentPath = f"{contentPath}\\Uploaded Content"

    if dir_info['separate_image_video']:
        os.makedirs(f"{contentPath}\\Images", exist_ok=True)
        os.makedirs(f"{contentPath}\\Videos", exist_ok=True)

    if captions or dir_info['caption_required']:
        os.makedirs(f"{contentPath}\\Captions", exist_ok=True)

    return contentPath


# Hash an image
def _hash_image(image):
    # Convert the image array to bytes and then create an sha256 hash
    return hashlib.sha256(image.tobytes()).hexdigest()


# Rename image using hash
def _generateContentHash(content):
    if content.content_type.split("/")[0] == "video":
        tempname = f'{_tempDirectory()}\\{content.filename}'
        content.save(tempname)

        vidcap = cv2.VideoCapture(tempname)
        success, image = vidcap.read()
        if success:
            hashable_image = Image.fromarray(image)

    elif content.content_type.split("/")[0] == "image":
        hashable_image = Image.open(content)

    return _hash_image(hashable_image)


# Upload a single image to the provided directory
def _uploadImage(image, fileDir, filename):
    image.seek(0)

    image.save(f'{fileDir}\\{filename}')


def _fixExtension(ext):
    ext_mapping = {'quicktime': 'mov'}

    if ext in ext_mapping:
        return ext_mapping[ext]
    else:
        return ext


# Handle the naming scheme of both video and image content
def _handleUploadTypeSemantics(contentPath, file, hash_string, separate_content):
    content_type, ext = file.content_type.split("/")

    ext = _fixExtension(ext)

    # Create new filename
    filename = f"{hash_string}.{ext}"

    # Place file in correct directory based on if content images and videos
    # should be separated
    if separate_content:
        existing_content = _tryListDir(f"{contentPath}\\Videos")
        existing_content.extend(_tryListDir(f"{contentPath}\\Images"))

        # Determine directory of file based on content type
        # Make first character of video or image uppercase, then add "s" to the end
        endDir = f"{contentPath}\\{content_type[0].upper()}{content_type[1:]}s"
    else:
        existing_content = _tryListDir(contentPath)
        endDir = contentPath
    
    # Return 1 if new image uploaded, otherwise return 0
    if filename in existing_content:
        return 0, filename, f"{endDir}\\{filename}"
        
    _uploadImage(file, endDir, filename)
    return 1, filename, f"{endDir}\\{filename}"


def uploadImages(search_dir, source_name, captions, files):
    dir_info = db.getUploadSearchDirectory(search_dir)

    if dir_info['search_dir_storage']:
        source_name = dir_info['section_directory']
        source_name = source_name.split("\\")[-1]

    # Create necessary paths for uploading content
    contentPath = _createDirectoryPath(dir_info, source_name, captions)

    newUploads, returnedFiles = 0, {}

    add_to_database = []

    for i, file in enumerate(files):
        sha256hash = _generateContentHash(file)

        newUpload, filename, file_loc = _handleUploadTypeSemantics(contentPath, file, sha256hash, dir_info['separate_image_video'])      

        # Save files in temp folder
        _uploadImage(file, f"{_tempDirectory()}", filename)

        try:
            # Upload meme to server
            returnedCaptions, duplicate_caption, caption_loc = _handleCaptionUpload(contentPath, sha256hash, captions[i], file.content_type.split('/')[-1].lower())
        except IndexError:
            returnedCaptions, duplicate_caption, caption_loc = [], False, None

        newUploads += newUpload

        if newUpload:
            file_hash = str(hash(file_loc))
            if caption_loc:
                add_to_database.append((hash(file_loc), filename, file.content_type.split("/")[0], file_loc, search_dir, source_name, dir_info['section_content_style'], 1, caption_loc, "", ""))
            else:                
                add_to_database.append((hash(file_loc), filename, file.content_type.split("/")[0], file_loc, search_dir, source_name, dir_info['section_content_style'], 0, "", "", ""))
        else:
            original_file = db.getDecodedData("SELECT * FROM shortContentData where content_loc=%s", [file_loc])[0]
            file_hash = original_file['content_id']


        # Add files to dictionary
        returnedFiles[file_hash] = {'file': f"{_tempDirectory(True)}/{filename}", 'type': file.content_type.split("/")[0], 'alt': f'Image from {source_name}', 'duplicate': not newUpload, 'duplicate_caption': duplicate_caption, 'captions': returnedCaptions}

    db.storeShortContent(add_to_database)

    return newUploads, returnedFiles


