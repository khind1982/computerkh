'''Top-level utilities and classes.'''
# pylint: disable = invalid-name

import json
import os
import sys
import time

import requests

import hms.utils as utils
from hms.payload import build_json
from hms.service import do_upload_or_locate_in_s3


class EEBFileSortController:  # pylint: disable = too-few-public-methods
    '''This class is used to ensure that images are sorted in the output in the
    correct order. We can't use simple string comparison to sort images, due to
    the naming scheme used for the cover/end/edge shots, which aren't in alpha-
    numerical order.
    '''

    # This controls sorting of the -000- image group, i.e. the covers and end shots.
    # We decorate filenames that end in one of the keys with the corresponding value
    # as a prefix, which then allows us to do normal string comparison to return the
    # files in the correct order.
    endshots = {
        '000-0000F': '01',
        '000-0000S': '02',
        '000-0000B': '03',
        '000-0000X': '04',
        '000-0000Y': '05',
        '000-0000Z': '06',
        '000-0000U': '07',
        '000-0000H': '08',
        '000-0001L': '09',
        '000-0002R': '10',
        '000-0003L': 'zza',
        '000-0004R': 'zzb',
        '000-0000V': 'zzz', # 'z' sorts after numbers and upper- and lower-case letters.
    }

    def __init__(self, imagedata):
        self.imagedata = imagedata
        self.imagename = self.imagedata['filename']
        _base_name = os.path.basename(self.imagename)
        _sort_base = os.path.splitext(_base_name)[0]
        _sort_chars = '-'.join(_sort_base.split('-')[-2:])
        if '_dpmi' in self.imagename:
            self.sortname = "0-%s" % _base_name
        elif _sort_chars in self.endshots.keys():
            self.sortname = "%s-%s" % (
                self.endshots[_sort_chars], _base_name)
        else:
            self.sortname = _base_name

    def __lt__(self, other):
        return self.sortname < other.sortname

    def __str__(self):
        return self.imagename


# Exceptions and errors
class HMSException(Exception):
    pass


class HMSAlreadyLoadedException(HMSException):
    pass


class HMSError(HMSException):
    def __init__(self, message):
        super(HMSError, self).__init__()
        self.message = message


class HMSStuckRequest(HMSError):
    pass


class HMSIncompleteRequest(HMSError):
    pass


class HMSUnknownFailure(HMSError):
    pass


class NotFoundError(Exception):
    def __init__(self, reply):  # pylint: disable = super-init-not-called
        self.status = reply.status_code
        self.message = reply.text


class DryrunException(Exception):
    def __init__(self, book_id, json, log):
        self.book_id = book_id
        self.json = json
        self.log = log

    def __str__(self):
        return "%s:\nJSON: %s\nHTTP log: %s\n" % (
            self.book_id, self.json, self.log)


def lookup(args, object_id):
    '''Send a Lookup request to HMS for the specified object_id. If we get
    back a non-empty JSON document, return it to the caller. Otherwise,
    return False to indicate the look up failed. Remember - HMS returns 200,
    even if we ask for something that doesn't exist...
    '''
    params = {
        "clientId": args.client_id,
        "uniqueId": utils.unique_book_id(object_id, args),
        "contentSetId": "AcaMedia"
    }
    lookup_url = '%s/%s' % (utils.get_hms_host(args), 'Lookup')
    reply = requests.get(lookup_url, params=params)

    if reply.status_code == 200:
        if reply.text == '[]':
            utils.debug(" Not Found")
            raise NotFoundError(reply)
        utils.debug(" Already loaded.")
        return json.loads(reply.text)
    elif reply.status_code == 400:
        if reply.text.startswith("Rejected "):
            raise HMSIncompleteRequest(reply.text)
    raise HMSUnknownFailure('Unknown HMS or local processing error')


def status(args, object_id):
    ''' Sned a Status request to HMS for the specified object_id
    The return value is either a text string indicating what's going on,
    or a JSON document showing the results'''
    params = {
        "clientId": args.client_id,
        "uniqueId": utils.unique_book_id(object_id, args),
        "contentSetId": "AcaMedia",
        "async": "Yes"
    }

    status_url = '%s/%s' % (utils.get_hms_host(args), 'Status')
    status = requests.get(status_url, params=params)

    if status.status_code == 400:
        # No object found in the status table. Raise NotFoundError
        raise NotFoundError(status)
    if status.status_code == 200:
        if "Stuck Request" in status.text:
            raise HMSStuckRequest("Stuck request. Try again.")
        if status.text.startswith("Processing not complete"):
            raise HMSIncompleteRequest(status.text)
        elif status.text.startswith("Status previously performed."):
            # If we get here, then we've already submitted a Status
            # request, and need to hit the Lookup endpoint for the
            # results.
            return lookup(args, object_id)
        else:
            # There may not be any JSON to decode here...
            return json.loads(status.text)
    if status.status_code == 500:
        # HMS is confused. Nothing we can do here, so bail.
        raise HMSError("HMS encountered an internal error: %s" % status.text)


def poll_status(args, object_id):
    '''Repeatedly call status() until we get back something we can use, or
    until HMS tells us it can't go on.
    '''
    while True:
        try:
            return status(args, object_id)
        except HMSIncompleteRequest as exc:
            utils.debug("Waiting: %s\n" % exc.message)
            time.sleep(20)


def poll_status_until_finished_or_failed(args, book_id):
    '''Poll the HMS Status endpoint until either we get back a JSON doc
    indicating a successful load request, or we catch one of the named
    exceptions. In either event, this is the end.'''
    utils.debug("Polling HMS for results...")
    try:
        utils.write_result(args, json.dumps(poll_status(args, book_id)))
        utils.debug(" Done\n")
        utils.debug("%s - load complete" % book_id)
    except HMSError as exc:
        print(exc.message, file=sys.stderr)
        # sys.exit(1)
    except NotFoundError as exc:
        print(exc.message, file=sys.stderr)
        # sys.exit(1)


def check_loaded_or_load_started(args, book_id):
    '''If the current book has already been loaded or recently submitted
    for loading, we can short-circuit the rest of the steps, and just use
    the JSON that HMS returns. If already loaded, the first block below will
    just write out the response from the HMS Lookup request and raise
    HMSAlreadyLoadedException. If the book was submitted recently in a
    different instance of the script, we poll the Status end point until we
    get a terminal state response - either success, in which case we get back
    the required JSON and can HMSAlreadyLoadedException, or an error condition,
    which may be recoverable, or may require the user to try the request again.
    The error message should make it clear which applies.'''
    if not args.force and not args.dryrun:
        try:
            lookup_data = lookup(args, book_id)
            utils.write_result(args, json.dumps(lookup_data))
            raise HMSAlreadyLoadedException
        except NotFoundError:
            utils.debug("Book %s not yet loaded\n" % book_id)
        except HMSIncompleteRequest as exc:
            utils.debug("Load already started: %s\n" % exc.message)
            utils.debug("Polling for status...\n")
            status = poll_status(args, book_id)
            utils.debug("Finished\n")
            utils.write_result(args, json.dumps(status))
            raise HMSAlreadyLoadedException

    if not args.dryrun:
        utils.debug("Checking HMS load status of %s..." % book_id)
        try:
            utils.write_result(args, json.dumps(poll_status(args, book_id)))
            utils.debug(" Loaded. Done\n")
            raise HMSAlreadyLoadedException
        except NotFoundError:
            if args.force:
                utils.debug(" Reload requested by user\n")
            else:
                utils.debug(" Not loaded. Proceeding.\n")
        except HMSError as exc:
            print("HMS internal error: %s" % exc.message, file=sys.stderr)
            raise


def do_dry_run(args, book_id, hms_request_body, post_url, params):
    if args.test_id:
        book_id = args.test_id

    dryrun_out = os.path.join(os.path.expanduser('~'), 'hmsloader_logs')
    os.makedirs(dryrun_out, exist_ok=True)

    dryrun_json = os.path.join(
        dryrun_out, '%s_dryrun.json' % book_id)

    dryrun_log = os.path.join(
        dryrun_out, '%s_dryrun.log' % book_id)

    pp_json = json.dumps(json.loads(hms_request_body), ensure_ascii=False, indent=4)
    with open(dryrun_json, 'w') as outf:
        outf.write(pp_json)
    with open(dryrun_log, 'w') as outf:
        outf.write("%s\n%s" % (post_url, params))
        # Raise an exception to break execution and ensure we don't go on
        # to submit the images when we were asked not to...
        raise DryrunException(book_id, dryrun_json, dryrun_log)


def prepare_and_post_request(args, load_results, book_id, bucket, copyright_text):
    '''Builds the JSON payload for the current book, prepares the query params
    and headers, and either submits to HMS for loading, or writes them out to
    disk if the user specified -d on the command line, denoting a dry run.'''
    load_results.sort(key=EEBFileSortController)
    hms_request_body = build_json(
            args, load_results, book_id, bucket, copyright_text)

    # Prepare the params and post_url here, so we can print them to file if we
    # are doing a dry run.
    headers = {}
    params = {
        'clientId': args.client_id,
        'uniqueId': utils.unique_book_id(book_id, args),
        'contentSetId': 'AcaMedia',
        'async': 'Yes',
        'action': 'Upsert'
    }

    post_url = '%s/%s' % (utils.get_hms_host(args), 'ComplexObject')

    if args.dryrun:
        # If the user requested a dry-run, call do_dryrun(), which raises
        # DryrunException to break the loop.
        do_dry_run(args, book_id, hms_request_body, post_url, params)

    utils.debug("Sending request to HMS...")
    post = requests.post(post_url, headers=headers, params=params,
                         data=hms_request_body)

    # If we get a failure message at this point, we shouldn't issue a Status
    # request, since that clears the transaction from the HMS results table,
    # making it unnecessarily difficult for the HMS devs to debug. Better is
    # to just quit at this point.

    try:
        post.raise_for_status()
    except requests.exceptions.HTTPError:
        utils.debug("HMS returned the following error message, and cannot continue:")
        utils.debug("\n")
        utils.debug(post.status_code)
        utils.debug(post.text)
        raise HMSError


    if args.stop_after_post:
        utils.debug("POST request sent, and stop_after_post specified.")
        with open("%s_post.json" % book_id, 'w') as outf:
            outf.write(post.text)
        sys.exit(4)


def handle_book(book_id, args):
    '''Takes a book ID and the command line arguments, and runs through the
    functions necessary to successfully load the book in HMS.'''

    copyright_text = utils.get_copyright(args, book_id)

    s3_profile = utils.get_s3_profile(args)
    bucket = utils.get_bucket(args)

    check_loaded_or_load_started(args, book_id)

    # We need to send a Status request to HMS, to make sure we don't clobber
    # a previous load attempt. If we get back 400, it means that no request has
    # been submitted yet for this book (if it had, and was already finished, the
    # call to lookup() above would have given us the JSON we need), so we can
    # submit a new request now.
    #
    # On the other hand, if we get 200, we need to test the response body as
    # well, since it can either be the JSON we want to indicate success, or a
    # message indicating what is happening with the request. If the message
    # includes the text "Stuck Request. Please Resubmit", we can do as it asks
    # and resubmit the request. This should clear the stuck request and start
    # again for this book. However, if we get any other message beginning with
    # "Processing not complete", we need to back off for a few seconds, then
    # try again.

    # poll_status() takes care of this for us, so we just need to catch
    # HMSStuckRequest and continue to load the book, or NotFoundError.


    files = utils.build_file_data(args, book_id)

    results = utils.do_checksums(args, files)

    load_results = do_upload_or_locate_in_s3(
            args, results, args.prefix, bucket, s3_profile)

    while True:
        try:
            prepare_and_post_request(
                args, load_results, book_id, bucket, copyright_text)

            poll_status_until_finished_or_failed(args, book_id)
        except HMSStuckRequest:
            continue
        else:
            break
