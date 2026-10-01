"""Generate the PDF fixtures used by backend and frontend tests.
Run: python scripts/make_fixture_pdfs.py
"""

from pathlib import Path

from fpdf import FPDF

OUTPUT_DIRS = [
    Path(__file__).parent.parent / "tests" / "fixtures",
    Path(__file__).parent.parent.parent / "frontend" / "e2e" / "fixtures",
]


def make_sample_contract() -> FPDF:
    pdf = FPDF()

    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, "Employment Contract\n\n")
    pdf.multi_cell(
        0, 10, "Notice period: The notice period is three months to the end of the month.\n"
    )
    pdf.multi_cell(0, 10, "Salary: The monthly gross salary is EUR 4,500.\n")

    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(
        0, 10, "Vacation: The employee receives 30 working days of paid vacation per year.\n"
    )
    pdf.multi_cell(0, 10, "Probation period: The probation period is six months.\n")

    return pdf


def make_empty() -> FPDF:
    pdf = FPDF()
    pdf.add_page()  # no text added: simulates a scanned PDF with no extractable text
    return pdf


def main() -> None:
    sample = make_sample_contract()
    empty = make_empty()

    for output_dir in OUTPUT_DIRS:
        output_dir.mkdir(parents=True, exist_ok=True)
        sample.output(str(output_dir / "sample_contract.pdf"))
        empty.output(str(output_dir / "empty.pdf"))
        print(f"wrote sample_contract.pdf and empty.pdf to {output_dir}")


if __name__ == "__main__":
    main()
