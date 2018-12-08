import datetime
import json
import hashlib
import os
import locale

from django.template import Template, Context
from django.conf import settings

import pdfkit
from num2words import num2words

from finance.models import Document


LOCAL_DIR = os.path.join(settings.BASE_DIR, 'finance', 'documents')
DATE_FORMAT = "%Y, %B %-d"


def get_loan_size(loan):
    integer, decimal = divmod(loan, 1)
    return int(integer), int(decimal * 100)


def get_verbose_loan_size(loan, lang):
    integer, decimal = divmod(loan, 1)
    return num2words(int(integer), lang=lang), num2words(int(decimal * 100), lang=lang)


def generate_file(document, lang='ru'):
    with open(os.path.join(LOCAL_DIR, 'templates', 'contract_{}.html'.format(lang))) as f:
        template = Template(f.read())
        context = Context(document)

        return template.render(context)


def get_hashes(doc):
    prev = Document.objects.order_by('date').last()
    if prev is not None:
        prev = prev.plain_document
    else:
        prev = ''
    block = ''.join([doc.plain_document for doc in Document.objects.order_by('-date')[:5]])
    prev_hash = hashlib.sha256(prev.encode('utf-8')).hexdigest()
    block_hash = hashlib.sha256(block.encode('utf-8')).hexdigest()
    doc['prev_hash'] = prev_hash
    doc['block_hash'] = block_hash
    text = json.dumps(doc)
    doc['own_hash'] = hashlib.sha256(text.encode('utf-8')).hexdigest()
    return doc


def create_document(debt):
    if debt.creditor.locale == 'ru':
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    elif debt.creditor.locale == 'en':
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    document = {
        "document_id": debt.id,
        "date": debt.created_at.strftime(DATE_FORMAT),
        "creditor_name": debt.creditor.full_name,
        "creditor_gender": debt.creditor.is_male,
        "borrower_name": debt.borrower.full_name,
        "borrower_gender": debt.borrower.is_male,
        "loan_size": get_loan_size(debt.loan_size),
        "verb_loan_size": get_verbose_loan_size(debt.loan_size, debt.creditor.locale),
        "percentage_year": float(round(debt.credit_percentage * 365, 2)),
        "percentage": float(debt.credit_percentage),
        "last_return_day": (debt.created_at + datetime.timedelta(hours=24 * debt.return_period)).strftime(DATE_FORMAT),
        "creditor_full_name": debt.creditor.full_name,
        "creditor_passport": debt.creditor.passport_number,
        "creditor_telephone": debt.creditor.telephone,
        "borrower_full_name": debt.borrower.full_name,
        "borrower_passport": debt.borrower.passport_number,
        "borrower_telephone": debt.borrower.telephone,
    }

    hashed_doc = get_hashes(document)
    Document.objects.create(plain_document=json.dumps(hashed_doc))
    html_file = generate_file(hashed_doc, lang=debt.creditor.locale)

    html_filename = os.path.join(LOCAL_DIR, 'htmls', str(debt.id) + '.html')
    pdf_filename = os.path.join(LOCAL_DIR, 'pdfs', str(debt.id) + '.pdf')
    with open(html_filename, 'w') as f:
        f.write(html_file)

    pdfkit.from_file(html_filename, pdf_filename)

    return pdf_filename
