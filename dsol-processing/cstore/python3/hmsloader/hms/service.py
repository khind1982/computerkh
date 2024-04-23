'''Functions for interacting with S3.

s3_head is for checking images are staged, s3_load is to stage images.
'''

import multiprocessing

import hms.utils as utils

import boto3
from botocore.exceptions import ClientError


def s3_head(head_data):
    '''Send a HEAD to S3 for an object. If we get a successful response, assume the
    file is correctly loaded and return its S3 key in the file_data structure.
    Otherwise, return an error message. We're not raising an exception, because
    they are not guaranteed to be picklable, which is a prerequisite of any
    values passed between processes participating in a multiprocessing system.
    '''
    file_data, prefix, bucket, s3_profile = head_data

    aws_session = boto3.session.Session(profile_name=s3_profile)
    s3_client = aws_session.client('s3')

    s3_key = "%s/%s" % (prefix, file_data['hashed_name'])

    try:
        # We don't need to keep head_object's reply - if we don't get a
        # ClientError exception, we know the object is loaded, if we do, then
        # return a flag value that indicates we need to load it.
        s3_client.head_object(
            Bucket=bucket,
            Key=s3_key,
        )
    except ClientError:
        return "NOT FOUND"

    file_data['s3_key'] = s3_key
    return file_data


def s3_load(load_data):
    '''Load the given file to S3, where `prefix' is the product code. Set the
    object's S3 key to `prefix/hashed_name'.
    '''

    # Short-circuit the loading process by calling s3_head. If it succeeds,
    # simply return the value it returns. Only do this if update_s3 is not
    # True for the file in question. If it IS True, we want to upload it
    # again to ensure we always send the most up to date version of the
    # file to HMS.

    file_data, prefix, bucket, s3_profile = load_data

    # If update_s3 is not set, issue a HEAD request to short circuit the rest
    # of the function. If it is set, we want to force updating the object, so
    # DO NOT want to isse HEAD, as this would potentially leave us using an
    # out of date version of the object.
    if not file_data['update_s3']:
        head = s3_head(load_data)
        if head != "NOT FOUND":
            return head

    aws_session = boto3.session.Session(profile_name=s3_profile)
    s3_svc = aws_session.resource('s3')
    s3_bucket = s3_svc.Bucket(bucket)

    s3_key = "%s/%s" % (prefix, file_data['hashed_name'])
    content_type = utils.mimetype(file_data['filename'])

    # upload_fileobj will take care of multipart uploads automatically, so we
    # can get the benefits of multithreading without the responsibility of
    # writing/maintaining it...
    with open(file_data['filename'], 'rb') as data:
        s3_bucket.upload_fileobj(
            data, s3_key, ExtraArgs={'ContentType': content_type})
    file_data['s3_key'] = s3_key

    # Use this for testing. It is single-threaded, so slower than the version
    # above using upload_fileobj, but easier to debug...
    # with open(file_data['filename'], 'rb') as data:
    #     reply = s3_bucket.put_object(
    #         Key=s3_key,
    #         Body=data,
    #         ContentType=content_type)
    # file_data['s3_key'] = reply.key

    return file_data


def do_upload_or_locate_in_s3(args, results, prefix, bucket, s3_profile):
    utils.debug("Uploading or locating files in S3...")
    s3pool = multiprocessing.Pool(processes=args.num_procs, maxtasksperchild=10)

    if args.s3_load_first:
        # We need to pass in all the information the child process needs
        # to set up the S3 connection
        func = s3_load
    else:
        # If the files are already on S3, we now need to send a HEAD to each
        # object, to ensure it's really there. If we find one missing, log it.
        # Store the S3 key in the file_data structure, so that whether we load
        # files or not, the next part of the script gets the same input.
        func = s3_head

    load_results = s3pool.map(
        func, [(f, prefix, bucket, s3_profile) for f in results])

    s3pool.close()
    s3pool.join()
    utils.debug(" Done\n")
    return load_results
