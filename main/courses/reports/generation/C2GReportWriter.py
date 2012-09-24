import csv
#import Console
from database import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SECURE_STORAGE_BUCKET_NAME
from storages.backends.s3boto import S3BotoStorage
from datetime import datetime, timedelta

class C2GReportWriterException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class C2GReportWriter:
    save_to_s3 = False
    txt_file = None
    csv_file = None
    csv_writer = None
    console = None
    
    def __init__(self, course, save_to_s3_arg):
        self.save_to_s3 = save_to_s3_arg
        if self.save_to_s3:
            course_prefix = course.handle.split('--')[0]
            course_suffix = course.handle.split('--')[1]
            dt = datetime.now()
            
            secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
            self.csv_file = secure_file_storage.open("%s/%s/reports/dashboard/csv/%02d_%02d_%02d__%02d_%02d_%02d-%s-Dashboard.csv" % (course_prefix, course_suffix, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix), 'wb')
            self.txt_file = secure_file_storage.open("%s/%s/reports/dashboard/txt/%02d_%02d_%02d__%02d_%02d_%02d-%s-Dashboard.txt" % (course_prefix, course_suffix, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix), 'wb')
            self.csv_writer = csv.writer(self.csv_file)
        #else:
            #self.console = Console.getconsole()
            
    def write(self, content=[], indent = 0, nl = 0):
        content_ = content
        content = [""] * indent
        for item in content_:
            if isinstance(item, (int, long)): content.append(str(item))
            elif isinstance(item, float): content.append("%.2f" % item)
            else: content.append(item)
        
        str_ =  "\t".join(content) + "\n"  
        
        if self.save_to_s3:
            self.csv_writer.write(content)
            self.txt_file.write(str_)
            if nl > 0:
                for i in range(nl):
                    self.csv_writer.write([""])
                    self.txt_file.write("\n")
        else:
            #console.write(str_)
            print str_
            if nl > 0:
                for i in range(nl):
                    #console.write("")
                    print ""
        
    def close(self):
        if self.save_to_s3:
            self.txt_file.close()
            self.csv_file.close()