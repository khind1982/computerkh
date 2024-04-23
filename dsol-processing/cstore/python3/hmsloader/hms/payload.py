'''Functions for constructing the JSON payload.'''
# pylint: disable = invalid-name

import json
import re

import hms
import hms.utils as utils


# pylint: disable = too-many-arguments
def build_json(args, data, book_id, bucket, copyright_text):
    '''Create the JSON body that will be sent to HMS to load the current book.
    '''

    # First of all, split the incoming data into separate lists of DPMI and
    # image files. This is necessary to ensure correct names in the output
    # where we need to add a sequence number to each item, and where each
    # type of item has its own enumeration. Split lists make it easier to
    # get this right.
    prefix = args.prefix
    client_id = args.client_id
    dpmi_files = [
        i for i in data
        if utils.is_dpmi_file(i['basename'])]

    image_files = [
        i for i in data
        if utils.is_image_type(i['basename'])]

    objects = [
        build_file_obj(f, i, bucket, prefix, copyright_text)
        for i, f in enumerate(dpmi_files, start=1)]

    objects.extend(
        build_file_obj(f, i, bucket, prefix, copyright_text)
        for i, f in enumerate(image_files, start=1))

    json_head = {
        "retrieveRecipe": "ComplexObject",
        "clientId": client_id,
        "action": "upsert",
        "contentSetId": "AcaMedia",
        "depends": "PARENT",
        "objects": objects,
        "children": build_pdf(image_files, book_id, copyright_text)
        }
    return json.dumps(json_head, ensure_ascii=False)


def build_pdf(image_files, book_id, copyright_text):
    '''Build the PDF specification for the book. Bound-with volumes are
    split into title-level parts, so each part only has to specify a single
    PDF.'''
    def is_cover(name):
        return name['basename'].startswith(re.sub('-\d{3}', '-000', book_id))

    covers = []
    internal_images = []

    for i in image_files:
        if is_cover(i):
            covers.append(i)
        else:
            internal_images.append(i)

    pdf_images = [
            utils.make_hms_img_name(n, i) for i,n in
            enumerate(
                sorted(
                    [*covers, *internal_images],
                    key=hms.EEBFileSortController), start=1)]

    return [pdf_template(book_id, pdf_images, copyright_text)]


def pdf_template(book_id, pdf_images, copyright_text):
    return {
        "childId": "EEB_CHILD",
        "objects": [
            {
                "type": "pdffrompages",
                "objectId": "EEB_%s_pdf_1" % book_id,
                "size": "NOTUSED",
                "md5": "NOTUSED",
                "location": "NOTUSED",
                "inputRef": pdf_images,
                "options": [
                    {
                        "key": "generateObject",
                        "value": "PFT",
                        "options": [
                            {
                                "key": "mimeType",
                                "value": "application/pdf",
                            },
                            {
                                "key": "Pdf_combineObjects",
                                "value": "INPUTREF",
                                "options": [
                                    {
                                        "key": "mimeType",
                                        "value": "image/jpeg"
                                    },
                                    {
                                        "key": "Image_convertObject",
                                        "value": "Yes"
                                    },
                                    {
                                        "key": "Image_quality",
                                        "value": "Yes",
                                        "options": [
                                            {
                                                "key": "Image_qualityValue",
                                                "value": "50"
                                            }
                                        ]
                                    },
                                    {
                                        "key": "Image_adaptiveresize",
                                        "value": "Yes",
                                        "options": [
                                            {
                                                "key": "Image_resizeValue",
                                                "value": "50"
                                            }
                                        ]
                                    },
                                    {
                                        "key": "Image_colorspace",
                                        "value": "Yes",
                                        "options": [
                                            {
                                                "key": "Image_colorspaceValue",
                                                "value": "RGB"
                                            }
                                        ]
                                    },
                                    {
                                        "key": "Image_addCustomCopyRight",
                                        "value": "Yes",
                                        "options": [
                                            {
                                                "key": "Image_customText",
                                                "value": copyright_text,
                                            },
                                        ]
                                    },
                                ]
                            },
                            {
                                "key": "Pdf_linearize",
                                "value": "Yes"
                            }
                        ]
                    }
                ]
            }
        ]
    }


def build_file_obj(file_data, idx, bucket, prefix, copyright_text):
    '''Build JSON subdocument for the passed set of file_data.
    '''
    f_size = file_data['size']
    f_md5 = file_data['md5']
    f_location = "https://%s.s3.amazonaws.com/%s/%s" % (
        bucket, prefix, file_data['hashed_name'])
    f_mimetype = utils.mimetype(file_data['hashed_name'])

    if file_data['file_type'] == 'dpmi':
        return {
            "type": "pagethread",
            "objectId": utils.make_dpmi_name(file_data, idx),
            "size": str(f_size),
            "md5": f_md5,
            "location": f_location,
            "options": [
                {
                    "key": "mimeType",
                    "value": f_mimetype,
                },
                # {
                #     "key": "validateObject",
                #     "value": "xml",
                # },
                {
                    "key": "generateObject",
                    "value": "DPMI",
                    "options": [
                        {
                            "key": "mimeType",
                            "value": "application/xml"
                        }
                    ]
                }
            ]
        }
    elif file_data['file_type'] == 'image':
        return {
            "type": "image",
            "objectId": utils.make_hms_img_name(file_data, idx),
            "size": str(f_size),
            "md5": f_md5,
            "location": f_location,
            "options": [
                {
                    "key": "mimeType",
                    "value": f_mimetype
                },
                {
                    "key": "validateObject",
                    "value": utils.image_type(file_data['basename']),
                },
                {
                    "key": "generateObject",
                    "value": "FULL",
                    "options": [
                        {
                            "key": "mimeType",
                            "value": "image/jpeg"
                        },
                        {
                            "key": "Image_convertObject",
                            "value": "Yes"
                        },
                        {
                            "key": "Image_addCustomCopyRight",
                            "value": "Yes",
                            "options": [
                                {
                                    "key": "Image_customText",
                                    "value": copyright_text,
                                },
                            ],
                        },
                        {
                            "key": "Image_quality",
                            "value": "Yes",
                            "options": [
                                {
                                    "key": "Image_qualityValue",
                                    "value": "90"
                                }
                            ]
                        }
                    ]
                },
                {
                    "key": "generateObject",
                    "value": "THUM",
                    "options": [
                        {
                            "key": "mimeType",
                            "value": "image/jpeg"
                        },
                        {
                            "key": "Image_convertObject",
                            "value": "Yes"
                        },
                        {
                            "key": "Image_scaleAs",
                            "value": "NDNP_THUMB"
                        }
                    ]
                }
            ]
        }
