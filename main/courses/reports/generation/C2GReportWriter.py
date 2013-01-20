import logging
import csv
import re
from cStringIO import StringIO
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SECURE_STORAGE_BUCKET_NAME
from storages.backends.s3boto import S3BotoStorage
from django.core.files.storage import default_storage
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
    
class C2GReportWriter:
    def __init__(self, save_to_s3_arg, s3_filepath = ''):
        self.save_to_s3 = save_to_s3_arg
        self.report_str = StringIO()
        self.csv_writer = csv.writer(self.report_str)
            
        if self.save_to_s3:
            self.s3_filepath = s3_filepath
            if AWS_SECURE_STORAGE_BUCKET_NAME == 'local': self.secure_file_storage = default_storage
            else: self.secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)

            
    def write(self, content=[], indent = 0, nl = 0):
        padded_content = [""] * indent
        for item in content:
            if isinstance(item, (int, long)): padded_content.append(str(item))
            elif isinstance(item, float): padded_content.append("%.2f" % item)
            else: padded_content.append(item)
        
        try:
            self.csv_writer.writerow(padded_content)
        except UnicodeEncodeError:
            logger.info("Failed to write row for file {0} due to unicode encode error.".format(self.s3_filepath))
            
        for i in range(nl): self.csv_writer.writerow([""])
        
    def writeout(self):
        content = self.report_str.getvalue()
        if self.save_to_s3:
            s3_file = self.secure_file_storage.open(self.s3_filepath, 'wb')
            s3_file.write(content)
            s3_file.close()
        
        return content
