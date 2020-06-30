from datetime import date, datetime
from pathlib import Path

import pytest
from jinja2 import Template

from juniorguru.models import Job
from juniorguru.send.send_metrics import create_message
from testing_utils import prepare_job_data


class JobMock():
    __names = dir(Job())

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            if name in self.__names:
                setattr(self, name, value)
            else:
                raise AttributeError(f"The Job model doesn't have '{name}'")


@pytest.fixture
def job_mock():
    data = prepare_job_data('123')
    return JobMock(effective_approved_at=data['approved_at'],
                   metrics=dict(users=15, pageviews=25, applications=3),
                   **data)


@pytest.fixture
def template():
    template_path = Path(__file__).parent.parent / 'juniorguru' / 'send' / 'templates' / 'metrics.html'
    return Template(template_path.read_text())


def test_create_message_metrics(job_mock, template):
    job_mock.metrics = dict(users=15, pageviews=25, applications=3)
    message = create_message(job_mock, template)
    html = message.get()['content'][0]['value']

    assert '<b>15</b>' in html
    assert '<b>25</b>' in html


def test_create_message_prefill_form(job_mock, template):
    job_mock.company_name = 'Honza Ltd.'
    message = create_message(job_mock, template)
    html = message.get()['content'][0]['value']

    assert '&entry.681099058=Honza+Ltd.' in html


def test_create_message_start_end(job_mock, template):
    job_mock.approved_at = date(2020, 6, 1)
    job_mock.effective_approved_at = date(2020, 6, 1)
    job_mock.expires_at = date(2020, 7, 1)
    message = create_message(job_mock, template, today=date(2020, 6, 23))
    html = message.get()['content'][0]['value']

    assert '22&nbsp;dní' in html
    assert 'schválen 1.6.2020' in html
    assert '8&nbsp;dní' in html
    assert 'vyprší 1.7.2020' in html


def test_create_message_newsletter_yes(job_mock, template):
    job_mock.newsletter_at = date(2020, 6, 1)
    message = create_message(job_mock, template, today=date(2020, 6, 23))
    html = message.get()['content'][0]['value']

    assert 'odeslán 1.6.2020' in html
    assert 'ANO' in html
    assert 'archiv' in html
    assert 'campaign-archive.com' in html


def test_create_message_newsletter_no(job_mock, template):
    job_mock.newsletter_at = None
    message = create_message(job_mock, template)
    html = message.get()['content'][0]['value']

    assert 'odeslán' not in html
    assert 'zatím NE' in html
    assert 'archiv' in html
    assert 'campaign-archive.com' in html


def test_create_message_applications_zero(job_mock, template):
    job_mock.metrics = dict(users=15, pageviews=25, applications=0)
    message = create_message(job_mock, template, today=date(2020, 6, 23))
    html = message.get()['content'][0]['value']

    assert 'uchazeč' not in html
    assert '<sup>' not in html


def test_create_message_applications_non_zero(job_mock, template):
    job_mock.metrics = dict(users=15, pageviews=25, applications=5)
    message = create_message(job_mock, template, today=date(2020, 6, 23))
    html = message.get()['content'][0]['value']

    assert 'uchazeč' in html
    assert '<b>5</b>' in html
    assert '<sup>' not in html
    assert 'května 2020' not in html


def test_create_message_applications_non_zero_note(job_mock, template):
    job_mock.effective_approved_at = date(2020, 1, 1)
    job_mock.metrics = dict(users=15, pageviews=25, applications=5)
    message = create_message(job_mock, template, today=date(2020, 6, 23))
    html = message.get()['content'][0]['value']

    assert 'uchazeč' in html
    assert '<b>5</b>' in html
    assert '<sup>' in html
    assert 'května 2020' in html


def test_create_message_expires_soon(job_mock, template):
    job_mock.expires_at = date(2020, 7, 1)
    message = create_message(job_mock, template, today=date(2020, 6, 26))
    html = message.get()['content'][0]['value']

    assert 'prodloužit o dalších 30&nbsp;dní' in html
    assert 'https://junior.guru/hire-juniors/#pricing' in html


def test_create_message_expires_not_soon(job_mock, template):
    job_mock.expires_at = date(2020, 7, 1)
    message = create_message(job_mock, template, today=date(2020, 6, 20))
    html = message.get()['content'][0]['value']

    assert 'prodloužit o dalších 30&nbsp;dní' not in html


def test_create_message_expires_soon_community(job_mock, template):
    job_mock.expires_at = date(2020, 7, 1)
    job_mock.pricing_plan = 'community'
    message = create_message(job_mock, template, today=date(2020, 6, 26))
    html = message.get()['content'][0]['value']

    assert 'komunitní' in html
    assert 'ZDARMA' in html


def test_create_message_expires_soon_community(job_mock, template):
    job_mock.expires_at = date(2020, 7, 1)
    job_mock.pricing_plan = 'standard'
    message = create_message(job_mock, template, today=date(2020, 6, 26))
    html = message.get()['content'][0]['value']

    assert '690&nbsp;Kč' in html
    assert 'https://junior.guru/hire-juniors/#handbook-pricing' in html