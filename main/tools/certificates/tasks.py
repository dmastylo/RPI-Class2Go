from celery import task
import os
from shutil import rmtree as util_rmtree
from storages.backends.s3boto import S3BotoStorage
import tempfile
try:
    import pdfkit
except ImportError, msg:
    pdfkit = False
try:
    from xhtml2pdf import pisa
except ImportError, msg:
    pisa = False

from django.conf import settings
from django.core.files.storage import default_storage
from django.template import Context, Template

from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SECURE_STORAGE_BUCKET_NAME


release_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)


def working_file():
    base = getattr(settings, 'FILE_UPLOAD_TEMP_DIR', '/tmp')
    return tempfile.mkstemp(prefix='tmpcert-', suffix='.pdf', dir=base)

def upload_certificate(tmp_path, outpath_prefix, path, outfile_name):
    if outpath_prefix:            # Local storage
        path = os.path.join(outpath_prefix, path)
        if os.path.isdir(path):
            util_rmtree(path)
        os.mkdir(path, 0700)
    else:                         # S3 storage
        default_storage.delete(path)

    storage_name = os.path.join(path, outfile_name)
    tmp_file = open(tmp_path, 'rb')
    storage = default_storage.open(storage_name, 'wb')
    storage.write(tmp_file.read())
    tmp_file.close()
    storage.close()
    return storage_name

@task
def certify(path_prefix, course, certificate, student, force_pdfkit=False):
    if not certificate.assets or not certificate.storage:
        raise ValueError("Certificate %s incorrectly specified; bad file paths" % str(certificate))
    # It is an error to call this method without an html to pdf renderer installed
    if not pisa and not pdfkit:
        raise ValueError("Certification cannot proceed without either xhtml2pdf or pdfkit installed.")

    # Asset prefix forced to local b/c xhtml2pdf can't read out of s3
    asset_prefix = getattr(settings, 'MEDIA_ROOT', '/')

    # Read in PDF template and set up render context
    infile_name = 'certificate-' + certificate.type + '.html'
    if not asset_prefix: asset_prefix = '/'      # NB: force local asset delivery
    infile_path = os.path.join(asset_prefix, certificate.assets, infile_name)
    unrendered_template = open(infile_path, 'rb').read()

    # Read in and render the template for this student name
    render_context = Context({'student_name': student.first_name + ' ' + student.last_name,
                              'basepath':     asset_prefix + '/' + certificate.assets + '/',
                             })
    pdf_src = Template(unrendered_template).render(render_context)

    # create the PDF in a safe temporary location
    tmp_handle, tmp_path = working_file()
    if pdfkit or force_pdfkit:
        pdf_gen_options = {'page-size': 'letter', 'encoding': 'UTF-8', 'orientation': 'landscape', 'margin-left': '0', 'margin-right': '0', 'margin-top': '0', 'margin-bottom': '0', 'quiet': ''}
        it_worked = pdfkit.from_string(input=pdf_src, output_path=tmp_path, options=pdf_gen_options)
        if not it_worked:
            # Except as far as I can tell, usually pdfkit will throw an exception and we'll die before we get here
            raise ValueError("PDFKit yielded error for user certification %s, %s" % (student.username, certificate.type))
    elif pisa:
        pdf_gen_status = pisa.CreatePDF(src=pdf_src, dest=os.fdopen(tmp_handle, 'wb'), path=os.path.join('/', path_prefix, certificate.assets))
        if pdf_gen_status.err:
            raise ValueError("PDF generation raised error code %s for user certification %s, %s" % (str(pdf_gen_status.err), student.username, certificate.type))

    # After file creation, move to s3 (or local)
    outfile_name = certificate.get_filename_by_user(student)
    return upload_certificate(tmp_path, path_prefix, certificate.storage, outfile_name)

@task
def makePDF(templatestr, path_prefix, course, certificate, student, context_in={}):
    # It is an error to call this method without an html to pdf renderer installed
    if not pisa and not pdfkit:
        raise ValueError("Certification cannot proceed without pdfkit installed.")

    # Render the template for this student name
    asset_prefix = getattr(settings, 'MEDIA_ROOT', '/')
    context_in.update({'student': student,
                    'student_name': student.first_name + ' ' + student.last_name,
                    'basepath':     os.path.join(asset_prefix, certificate.assets, ''), })
    render_context = Context(context_in)
    pdf_src = Template(templatestr).render(render_context)

    # create the PDF in a safe temporary location
    tmp_handle, tmp_path = working_file()
    pdf_gen_options = {'page-size': 'letter', 'encoding': 'UTF-8', 'orientation': 'landscape', 'margin-left': '0', 'margin-right': '0', 'margin-top': '0', 'margin-bottom': '0', 'quiet': ''}
    it_worked = pdfkit.from_string(input=pdf_src, output_path=tmp_path, options=pdf_gen_options)
    if not it_worked:
        # Except as far as I can tell, usually pdfkit will throw an exception and we'll die before we get here
        raise ValueError("PDFKit yielded error for user certification %s, %s" % (student.username, certificate.type))

    # After file creation, move to s3 (or local)
    outfile_name = certificate.get_filename_by_user(student)
    return upload_certificate(tmp_path, path_prefix, certificate.storage, outfile_name)

