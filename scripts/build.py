import xmltodict
import json
import os
import hashlib
from lxml import etree
import sys

# Define file paths
XML_PATH = './data/manuscript.xml'
DTD_PATH = './data/schema.dtd'
JSON_OUT = './public/data/manuscript.json'
VERSION_OUT = './public/data/version.json'

def build_pipeline():
    print("Starting Data Pipeline...")

    # Step 1: Strict Validation
    try:
        with open(DTD_PATH, 'rb') as dtd_file:
            dtd = etree.DTD(dtd_file)
        with open(XML_PATH, 'rb') as xml_file:
            xml_doc = etree.parse(xml_file)

        if not dtd.validate(xml_doc):
            print("Validation Failed! The XML violates the schema:")
            for error in dtd.error_log:
                print(f"Line {error.line}: {error.message}")
            sys.exit(1) # This tells GitHub Actions to STOP and mark the build as failed
            
        print("XML is valid.")

    except Exception as e:
        print(f"❌ System error during validation: {e}")
        sys.exit(1)

    # Step 2: Transformation & Versioning
    try:
        with open(XML_PATH, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        # Calculate MD5 Hash for versioning
        version_hash = hashlib.md5(xml_content.encode('utf-8')).hexdigest()

        # Convert to Dictionary
        data_dict = xmltodict.parse(xml_content, attr_prefix='@_')

        # Ensure directories exist
        os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)

        # Save Manuscript JSON
        with open(JSON_OUT, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=None)

        # Save Version JSON
        with open(VERSION_OUT, 'w', encoding='utf-8') as f:
            json.dump({"version": version_hash}, f)

        print(f"Build successful! Version: {version_hash}")

    except Exception as e:
        print(f"Transformation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_pipeline()
