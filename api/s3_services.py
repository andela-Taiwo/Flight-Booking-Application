import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import mimetypes

from django.conf import settings
from django.db import transaction
from user.models import Profile


def s3_encode_metadata(s):
    out_string = ''
    for c in s:
        if ord(c) == 92:  # character = \
            out_string += '\\0x5c\\'
        elif ord(c) > 127:
            safe_ord = str(hex(ord(c)))
            out_string += '\\'+safe_ord+'\\'
        else:
            out_string += c
    return out_string


def s3_decode_metadata(s):
    out_string = ''
    i = 0
    s = s.replace('\.', '.')
    l = len(s)
    while i < l:
        c = s[i]
        if ord(c) == 92:
            i += 1  # Skip \
            h = ''
            while ord(s[i]) != 92:
                h += s[i]
                i += 1
            out_string += chr(int(h, 16))  # Decode hex character
            # Last \ will be skipped by += 1 at the bottom of the loop
        else:
            out_string += c
        i += 1

    return out_string


def s3_get_resource():
    s3 = boto3.resource(
        's3',
        settings.S3_REGION,
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'}
        )
    )
    return s3


def s3_get_bucket(bucket_name):
    s3 = s3_get_resource()
    bucket = s3.Bucket(bucket_name)
    return bucket


def s3_get_client():
    try:
        client = boto3.client(
            's3',
            settings.S3_REGION,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            config=Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'}
            )
        )
        return client
    except ClientError as e:
        print("Couldn't establish S3 client connection: ", e)
        return None


def s3_upload(*, filekey, filebody, filename, uploader_pk, description):

    bucket = s3_get_bucket(settings.S3_BUCKET_NAME)

    if description == '':
        description = filename

    mimetypes.init()
    content_type, content_encoding = mimetypes.guess_type(filename)
    if not content_type:
        content_type = 'application/binary'
    if not content_encoding:
        content_encoding = ''

    s3obj = bucket.put_object(
        Body=filebody,
        ContentDisposition='attachment; filename={}'.format(filename),
        # ContentEncoding='string',
        # ContentLanguage='string',
        ContentType=content_type,
        Key=filekey,
        Metadata={
            'uploader_pk': '{}'.format(uploader_pk),
            'description': s3_encode_metadata(description),
            'filename': s3_encode_metadata(filename),
        }
    )

    return s3obj


def s3_delete(filekeys):

    bucket = s3_get_bucket(settings.S3_BUCKET_NAME)
    objects = []
    keys = []

    for key in filekeys:
        if key.startswith('/'):
            filekey = key[1:]
        else:
            filekey = key

        keys.append(filekey)
        objects.append({'Key': filekey})

    try:
        response = bucket.delete_objects(
            Delete={
                'Objects': objects,
                'Quiet': False
            }
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            with transaction.atomic():
                file = Profile.objects.filter(s3_key=key)
                if file.count():
                    file.delete()
                else:
                    print("Couldn't find file {} in Profile table".format(key))
            return True
        else:
            # Something happened with S3
            # Let's do nothing
            return False
    except:
        # Something happened with S3
        # Let's do nothing
        return False


def s3_presigned_url(file_key):
    # generate signed download url
    s3client = s3_get_client()
    url = s3client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': settings.S3_BUCKET_NAME,
            'Key': file_key
        }
    )
    return url
