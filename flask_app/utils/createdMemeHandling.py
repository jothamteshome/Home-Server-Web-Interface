import os

from flask_app.utils.imageUploading import _generateContentHash, _uploadImage
from flask_app.utils.globalUtils import _tempDirectory, _openJSONDirectoriesFile


def _retreiveMemeCaptions(content_hash, existingOnly=False):
    CAPTION_DIR = _openJSONDirectoriesFile()['conditionally-included-routes']['finalized-memes-dirs']['text-directory']
    returnedCaptions = []
    existingCaptions = set()

    try:
        with open(f"{CAPTION_DIR}\\{content_hash}.txt", "r") as captionFile:
            for line in captionFile:
                line = line.strip()
                returnedCaptions.append("\n\n".join(line.split("***")))
                existingCaptions.add(line)
    except FileNotFoundError:
        pass

    if existingOnly:
        return returnedCaptions
    
    return returnedCaptions, existingCaptions

def _handleCaptionUpload(content_hash, caption):
    CAPTION_DIR = _openJSONDirectoriesFile()['conditionally-included-routes']['finalized-memes-dirs']['text-directory']
    os.makedirs(CAPTION_DIR, exist_ok=True)

    returnedCaptions, existingCaptions = _retreiveMemeCaptions(content_hash)
    duplicate = True


    # Write caption to file
    with open(f"{CAPTION_DIR}\\{content_hash}.txt", "a") as captionFile:
        caption = caption.replace('\r\n', '***').replace('\n', '***').replace('•••', '***')

        # Only write captions if they do not exist yet
        if caption not in existingCaptions:
            captionFile.write(f"{caption}\n")
            returnedCaptions.append("\n\n".join(caption.split("***")))
            duplicate = False

    return returnedCaptions, duplicate


def _uploadMeme(image, caption):
    IMAGE_DIR = _openJSONDirectoriesFile()['conditionally-included-routes']['finalized-memes-dirs']['image-directory']
    os.makedirs(IMAGE_DIR, exist_ok=True)

    # Generate new meme name
    ext = image.content_type.split('/')[-1]
    content_hash = _generateContentHash(image)
    filename = f"{content_hash}.{ext}"

    # Save image to file
    _uploadImage(image, IMAGE_DIR, filename)
    _uploadImage(image, _tempDirectory(), filename)   

    # Upload meme to server
    captions, duplicate_caption = _handleCaptionUpload(content_hash, caption)

    return content_hash, duplicate_caption,\
        {filename: {'file': f"{_tempDirectory(True)}/{filename}", 'type': image.content_type.split("/")[0], 
                    'captions': captions, 'duplicate': duplicate_caption}}
