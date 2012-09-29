import csv
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SECURE_STORAGE_BUCKET_NAME
from storages.backends.s3boto import S3BotoStorage
from django.core.files.storage import default_storage
from datetime import datetime, timedelta

class C2GReportWriterException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class C2GReportWriter:
    save_to_s3 = False
    csv_file = None
    csv_writer = None
    
    def __init__(self, course, save_to_s3_arg, s3_filepath):
        self.save_to_s3 = save_to_s3_arg
        if self.save_to_s3:
            if AWS_SECURE_STORAGE_BUCKET_NAME == 'local':
                secure_file_storage = default_storage
            else: 
                secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
            
            self.csv_file = secure_file_storage.open(s3_filepath, 'wb')
            self.csv_writer = csv.writer(self.csv_file)
            
    def write(self, content=[], indent = 0, nl = 0):
        content_ = content
        content = [""] * indent
        for item in content_:
            if isinstance(item, (int, long)): content.append(str(item))
            elif isinstance(item, float): content.append("%.2f" % item)
            else: content.append(item)
        
        if self.save_to_s3:
            self.csv_writer.writerow(content)
            if nl > 0:
                for i in range(nl): self.csv_writer.writerow([""])
        else:
            print "\t".join(content) + "\n"
            if nl > 0:
                for i in range(nl): print ""
        
    def close(self):
        if self.save_to_s3:
			self.csv_file.close()