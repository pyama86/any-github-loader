import google.cloud.dlp
from google.cloud.dlp import CharsToIgnore
from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader
import os
import sys
import csv
import codecs
import tempfile
import argparse

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--project", type=str, required=False)
    parser.add_argument("--mask", type=bool, default=False)
    args = parser.parse_args()
    return(args)

def mask_content(project, input_str, info_types, masking_character=None, number_to_mask=0, ignore_commpn=None):
    dlp = google.cloud.dlp_v2.DlpServiceClient()
    parent = f"projects/{project}"
    item = {"value": input_str}

    inspect_config = {"info_types": [{"name": info_type} for info_type in info_types]}
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "primitive_transformation": {
                        "character_mask_config": {
                            "masking_character": masking_character,
                            "number_to_mask": number_to_mask,
                            "characters_to_ignore":[{
                                "common_characters_to_ignore": ignore_commpn
                            }]
                        }
                    }
                }
            ]
        }
    }

    response = dlp.deidentify_content(
        request={
            "parent": parent,
            "deidentify_config": deidentify_config,
            "inspect_config": inspect_config,
            "item": item,
        }
    )
    return response.item.value

def main():
    args = get_args()
    if os.environ.get('OPENAI_API_KEY') is None:
        print('Please set OPENAI_API_KEY')
        sys.exit(1)
    if args.mask:
        if args.project is None:
            print('Please set project id')
            sys.exit(1)

        GCP_PROJECT = args.project
        print('GCP_PROJECT is {}'.format(GCP_PROJECT))

    filename = 'contents.csv'
    file_cnt = 0
    tmpdir = tempfile.mkdtemp()
    print("data directory: {}".format(tmpdir))

    with open(filename, 'r') as f:
        try:
            for rows in csv.reader(f):
                for row in rows:
                        if args.mask:
                            data = mask_content(GCP_PROJECT, row, ['PERSON_NAME',
                                                                             'EMAIL_ADDRESS',
                                                                             'PHONE_NUMBER',
                                                                             'CREDIT_CARD_NUMBER',
                                                                             'LOCATION',
                                                                             'MALE_NAME',
                                                                             'FEMALE_NAME',
                                                                             'AUTH_TOKEN',
                                                                             'AWS_CREDENTIALS',
                                                                             'BASIC_AUTH_HEADER',
                                                                             'GCP_API_KEY',
                                                                             'ENCRYPTION_KEY',
                                                                             'GCP_CREDENTIALS',
                                                                             'OAUTH_CLIENT_SECRET',
                                                                             'PASSWORD',
                                                                             'JAPAN_BANK_ACCOUNT'
                                                                             ],
                                                       masking_character='*',
                                                       ignore_commpn=CharsToIgnore.CommonCharsToIgnore.PUNCTUATION.value)
                        else:
                            data = row
                        file_dst = os.path.join(tmpdir, '{}.txt'.format(file_cnt))
                        file_cnt += 1
                        f = open(file_dst, 'w')
                        f.write(data)
                        f.close()
        except Exception as e:
            print(e)

    documents = SimpleDirectoryReader(tmpdir).load_data()
    print('start indexing')
    index = GPTSimpleVectorIndex(documents)
    index.save_to_disk('index.json')
    print('finish indexing')

if __name__ == "__main__":
    main()
