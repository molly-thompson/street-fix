"""Tests for site visit reports and their photos."""

from collections.abc import Callable

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from employees.organisation_models import Employee
from employees.work_models import WorkItem, WorkItemPhoto, WorkItemReport

pytestmark = pytest.mark.django_db

PHOTO_URL = "https://example.com/photo.jpg"

MakeReport = Callable[..., WorkItemReport]


@pytest.fixture
def make_report(
    make_employee: Callable[..., Employee],
    make_work_item: Callable[..., WorkItem],
) -> MakeReport:
    """Provide a factory for draft reports on new work items."""

    def make(**fields: object) -> WorkItemReport:
        return WorkItemReport.objects.create(
            work_item=make_work_item(),
            employee=make_employee(),
            **fields,
        )

    return make


def add_photo(report: WorkItemReport, tag: str) -> WorkItemPhoto:
    """Attach a photo to a report."""
    return WorkItemPhoto.objects.create(
        work_item_report=report,
        uploaded_by=report.employee,
        tag=tag,
        image_url=PHOTO_URL,
    )


def test_new_report_is_a_draft(make_report: MakeReport) -> None:
    """A report is not submitted until submit is called."""
    report = make_report()

    assert not report.is_submitted
    assert report.extra_answers == {}


def test_submit_with_before_photo(make_report: MakeReport) -> None:
    """A complete report with a before photo can be submitted."""
    report = make_report(outcome="FIXED", work_done="Filled and sealed pothole")
    add_photo(report, WorkItemPhoto.Tag.BEFORE)

    report.submit()

    assert report.is_submitted


def test_submit_with_reason_instead_of_before_photo(make_report: MakeReport) -> None:
    """A written reason can stand in for the before photo."""
    report = make_report(
        outcome="NO_ACCESS",
        no_before_photo_reason="Road closed by police on arrival",
    )

    report.submit()

    assert report.is_submitted


def test_cannot_submit_without_before_photo_or_reason(make_report: MakeReport) -> None:
    """The before photo rule blocks submission."""
    report = make_report(outcome="FIXED", work_done="Filled pothole")
    add_photo(report, WorkItemPhoto.Tag.AFTER)

    with pytest.raises(ValidationError) as error:
        report.submit()

    assert "no_before_photo_reason" in error.value.message_dict
    assert not report.is_submitted


def test_fixed_outcome_needs_work_done(make_report: MakeReport) -> None:
    """A fixed report must say what was done."""
    report = make_report(outcome="FIXED", no_before_photo_reason="Camera broken")

    assert "work_done" in report.submission_errors()


def test_further_work_outcome_must_flag_further_work(make_report: MakeReport) -> None:
    """The further work outcome and flag must agree."""
    report = make_report(outcome="FURTHER_WORK", no_before_photo_reason="Dark")

    assert "further_work_needed" in report.submission_errors()


def test_report_cannot_be_submitted_twice(make_report: MakeReport) -> None:
    """Submitting again is refused."""
    report = make_report(outcome="NO_FAULT_FOUND", no_before_photo_reason="n/a")
    report.submit()

    with pytest.raises(ValidationError):
        report.submit()


def test_photo_tag_must_be_before_or_after(make_report: MakeReport) -> None:
    """The database rejects any other photo tag."""
    report = make_report()

    with pytest.raises(IntegrityError), transaction.atomic():
        add_photo(report, "DURING")
