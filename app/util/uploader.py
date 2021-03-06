import os
import datetime
from google.cloud import storage
from nanoid import generate
from werkzeug.utils import secure_filename


IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
GRAPHIC_EXTENSIONS = set(['fbx', 'glb', 'gltf'])
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS.union(GRAPHIC_EXTENSIONS)


def upload(object_file):
    """
    Upload object to cloud storage
    In this app, mostly it'll be fbx, glTF, jpeg
    """
    client = storage.Client()
    bucket = client.get_bucket(os.environ.get('BUCKET'))
    # Nano id(Better uuid) + timestamp + file extension
    timestamp = int(datetime.datetime.now().timestamp() * 10**6)
    destination_blob_name = "{}_{}.{}".format(
            generate(size=32),
            str(timestamp),
            file_extension(secure_filename(object_file.filename)))
    blob = bucket.blob(destination_blob_name)
    content_type = object_file.content_type
    if file_extension(secure_filename(object_file.filename)) in GRAPHIC_EXTENSIONS:
        content_type = _determine_graphic_content_type(object_file.filename)
    # TODO: Change fbx blob to glTF and save both.
    blob.upload_from_file(object_file, content_type=content_type)
    return blob


def allowed_file(filename):
    """
    Check whether file extension is allowed
    """
    return '.' in filename and \
           file_extension(filename) in ALLOWED_EXTENSIONS


def file_extension(filename):
    """
    Get file extension from filename
    """
    return filename.rsplit('.', 1)[1].lower()


def _determine_graphic_content_type(filename):
    """
    Determine content type of graphic model(fbx, glb, or glTF)
    """
    extension = file_extension(secure_filename(filename))
    content_type = 'application/octet-stream'
    if extension == 'fbx':
        # TODO: Change when fbx gets a mime type
        content_type = 'application/octet-stream'
    elif extension == 'glb':
        content_type = 'model/gltf-binary'
    elif extension == 'gltf':
        content_type = 'model/gltf+json'
    return content_type

