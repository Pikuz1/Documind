"""Generate the synthetic German employment contract used by the retrieval evaluation.
Run from backend/: python -m scripts.make_eval_contract
"""

from pathlib import Path

from fpdf import FPDF

OUTPUT = Path(__file__).resolve().parent.parent / "eval" / "arbeitsvertrag.pdf"

INTRO = (
    "zwischen der Nordlicht Software GmbH, Hafenstraße 12, 20457 Hamburg (nachfolgend "
    '"Arbeitgeber") und Frau Lena Weber, Lindenallee 5, 22767 Hamburg (nachfolgend '
    '"Arbeitnehmerin") wird folgender Arbeitsvertrag geschlossen.'
)

# One inner list per PDF page, so every clause's page number is known for the golden set.
PAGES: list[list[tuple[str, list[str]]]] = [
    [
        (
            "§ 1 Beginn des Arbeitsverhältnisses",
            [
                "(1) Das Arbeitsverhältnis beginnt am 1. März 2026 und wird auf unbestimmte "
                "Zeit geschlossen.",
                "(2) Vor Beginn des Arbeitsverhältnisses ist eine ordentliche Kündigung "
                "ausgeschlossen.",
            ],
        ),
        (
            "§ 2 Tätigkeit und Arbeitsort",
            [
                "(1) Die Arbeitnehmerin wird als Senior Softwareentwicklerin im Bereich "
                "Plattformentwicklung eingestellt. Zu ihren Aufgaben gehören insbesondere die "
                "Konzeption, Entwicklung und Wartung von Webanwendungen sowie die fachliche "
                "Betreuung von Nachwuchskräften.",
                "(2) Der Arbeitgeber ist berechtigt, der Arbeitnehmerin auch andere zumutbare "
                "Tätigkeiten zuzuweisen, die ihren Kenntnissen und Fähigkeiten entsprechen.",
                "(3) Arbeitsort ist der Firmensitz in Hamburg. Der Arbeitgeber behält sich vor, "
                "die Arbeitnehmerin vorübergehend an einem anderen Standort des Unternehmens in "
                "Deutschland einzusetzen, sofern dies der Arbeitnehmerin zumutbar ist.",
                "(4) Die Arbeitnehmerin berichtet an die Leitung der Abteilung "
                "Plattformentwicklung.",
            ],
        ),
    ],
    [
        (
            "§ 3 Probezeit",
            [
                "(1) Die ersten sechs Monate des Arbeitsverhältnisses gelten als Probezeit.",
                "(2) Während der Probezeit kann das Arbeitsverhältnis von beiden Seiten mit einer "
                "Frist von zwei Wochen gekündigt werden.",
            ],
        ),
        (
            "§ 4 Arbeitszeit",
            [
                "(1) Die regelmäßige wöchentliche Arbeitszeit beträgt 40 Stunden. Die Verteilung "
                "auf die einzelnen Wochentage richtet sich nach den betrieblichen Regelungen; in "
                "der Regel wird von Montag bis Freitag gearbeitet.",
                "(2) Es gilt Gleitzeit mit einer Kernarbeitszeit von 10:00 bis 15:00 Uhr.",
                "(3) Beginn und Ende der täglichen Arbeitszeit sowie die Pausen richten sich nach "
                "den Bestimmungen des Arbeitszeitgesetzes.",
            ],
        ),
        (
            "§ 5 Überstunden",
            [
                "(1) Die Arbeitnehmerin ist verpflichtet, bei betrieblicher Notwendigkeit im "
                "gesetzlich zulässigen Rahmen Überstunden zu leisten.",
                "(2) Überstunden werden vorrangig durch Freizeit ausgeglichen. Ist ein "
                "Freizeitausgleich innerhalb von drei Monaten nicht möglich, werden die "
                "Überstunden mit dem anteiligen Stundenlohn vergütet.",
                "(3) Mit dem Gehalt sind bis zu fünf Überstunden pro Monat abgegolten.",
            ],
        ),
    ],
    [
        (
            "§ 6 Vergütung",
            [
                "(1) Die Arbeitnehmerin erhält ein monatliches Bruttogehalt in Höhe von 5.200 EUR.",
                "(2) Die Vergütung ist jeweils am letzten Bankarbeitstag des Monats fällig und "
                "wird auf ein von der Arbeitnehmerin benanntes Konto überwiesen.",
                "(3) Das Gehalt wird jährlich zum 1. April überprüft. Ein Anspruch auf Erhöhung "
                "besteht nicht.",
            ],
        ),
        (
            "§ 7 Sonderzahlungen",
            [
                "(1) Die Arbeitnehmerin erhält ein Weihnachtsgeld in Höhe von 50 Prozent eines "
                "Bruttomonatsgehalts, das mit dem Novembergehalt ausgezahlt wird.",
                "(2) Darüber hinaus kann ein jährlicher Bonus von bis zu 10 Prozent des "
                "Jahresbruttogehalts gezahlt werden, dessen Höhe sich nach der Erreichung "
                "individueller und unternehmensbezogener Ziele richtet. Die Ziele werden jeweils "
                "zu Beginn des Geschäftsjahres schriftlich vereinbart.",
                "(3) Der Arbeitgeber gewährt einen monatlichen Zuschuss zum Deutschlandticket in "
                "Höhe von 30 EUR.",
            ],
        ),
    ],
    [
        (
            "§ 8 Urlaub",
            [
                "(1) Die Arbeitnehmerin hat Anspruch auf einen jährlichen Erholungsurlaub von "
                "30 Arbeitstagen bei einer Fünf-Tage-Woche.",
                "(2) Der Urlaub ist grundsätzlich im laufenden Kalenderjahr zu nehmen. Eine "
                "Übertragung auf das nächste Kalenderjahr ist nur bis zum 31. März zulässig.",
                "(3) Im Ein- und Austrittsjahr besteht für jeden vollen Monat des "
                "Arbeitsverhältnisses Anspruch auf ein Zwölftel des Jahresurlaubs.",
            ],
        ),
        (
            "§ 9 Arbeitsverhinderung und Krankheit",
            [
                "(1) Die Arbeitnehmerin ist verpflichtet, dem Arbeitgeber jede "
                "Arbeitsverhinderung und deren voraussichtliche Dauer unverzüglich, spätestens "
                "bis 9:00 Uhr am ersten Tag, mitzuteilen.",
                "(2) Bei einer Arbeitsunfähigkeit infolge Krankheit, die länger als drei "
                "Kalendertage dauert, ist spätestens am darauffolgenden Arbeitstag eine ärztliche "
                "Bescheinigung vorzulegen.",
                "(3) Im Krankheitsfall wird das Gehalt nach den Bestimmungen des "
                "Entgeltfortzahlungsgesetzes für die Dauer von bis zu sechs Wochen fortgezahlt.",
            ],
        ),
    ],
    [
        (
            "§ 10 Nebentätigkeit",
            [
                "(1) Jede entgeltliche Nebentätigkeit bedarf der vorherigen schriftlichen "
                "Zustimmung des Arbeitgebers.",
                "(2) Die Zustimmung wird erteilt, wenn die Nebentätigkeit die Arbeitsleistung "
                "nicht beeinträchtigt und nicht in Konkurrenz zum Arbeitgeber steht.",
            ],
        ),
        (
            "§ 11 Verschwiegenheit",
            [
                "(1) Die Arbeitnehmerin verpflichtet sich, über alle Betriebs- und "
                "Geschäftsgeheimnisse sowie vertrauliche Kundendaten Stillschweigen zu bewahren.",
                "(2) Diese Pflicht gilt auch nach Beendigung des Arbeitsverhältnisses fort.",
                "(3) Bei Beendigung des Arbeitsverhältnisses sind alle geschäftlichen Unterlagen, "
                "Datenträger und Arbeitsmittel, insbesondere Laptop und Zugangskarten, "
                "unaufgefordert zurückzugeben.",
            ],
        ),
        (
            "§ 12 Mobiles Arbeiten",
            [
                "(1) Die Arbeitnehmerin kann bis zu drei Tage pro Woche mobil, insbesondere von "
                "zu Hause aus, arbeiten.",
                "(2) Die Tage im Büro werden mit der Teamleitung abgestimmt. Für die Ausstattung "
                "des häuslichen Arbeitsplatzes zahlt der Arbeitgeber einmalig eine Pauschale von "
                "500 EUR.",
            ],
        ),
    ],
    [
        (
            "§ 13 Kündigung",
            [
                "(1) Nach Ablauf der Probezeit beträgt die Kündigungsfrist für beide Seiten drei "
                "Monate zum Monatsende.",
                "(2) Verlängert sich die gesetzliche Kündigungsfrist für den Arbeitgeber, gilt "
                "die verlängerte Frist auch für die Kündigung durch die Arbeitnehmerin.",
                "(3) Die Kündigung bedarf der Schriftform; eine Kündigung per E-Mail ist "
                "unwirksam.",
                "(4) Das Arbeitsverhältnis endet ohne Kündigung mit Ablauf des Monats, in dem die "
                "Arbeitnehmerin die Regelaltersgrenze erreicht.",
            ],
        ),
        (
            "§ 14 Nachvertragliches Wettbewerbsverbot",
            [
                "(1) Für die Dauer von zwölf Monaten nach Beendigung des Arbeitsverhältnisses "
                "darf die Arbeitnehmerin nicht für ein Unternehmen tätig werden, das mit dem "
                "Arbeitgeber in direktem Wettbewerb steht.",
                "(2) Für die Dauer des Wettbewerbsverbots zahlt der Arbeitgeber eine "
                "Karenzentschädigung in Höhe von 50 Prozent der zuletzt bezogenen "
                "vertragsmäßigen Leistungen.",
            ],
        ),
        (
            "§ 15 Ausschlussfristen",
            [
                "Ansprüche aus dem Arbeitsverhältnis verfallen, wenn sie nicht innerhalb von drei "
                "Monaten nach Fälligkeit schriftlich geltend gemacht werden.",
            ],
        ),
        (
            "§ 16 Schlussbestimmungen",
            [
                "Änderungen und Ergänzungen dieses Vertrages bedürfen der Schriftform. Sollte "
                "eine Bestimmung unwirksam sein, bleibt die Wirksamkeit der übrigen Bestimmungen "
                "unberührt.",
            ],
        ),
    ],
]


def write_paragraph(pdf: FPDF, text: str, style: str = "", gap: float = 2) -> None:
    pdf.set_font("Helvetica", style=style, size=11)
    pdf.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(gap)


def main() -> None:
    pdf = FPDF()
    for index, sections in enumerate(PAGES):
        pdf.add_page()
        if index == 0:
            write_paragraph(pdf, "ARBEITSVERTRAG", style="B", gap=4)
            write_paragraph(pdf, INTRO, gap=4)
        for heading, paragraphs in sections:
            write_paragraph(pdf, heading, style="B", gap=1)
            for paragraph in paragraphs:
                write_paragraph(pdf, paragraph)
            pdf.ln(2)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"wrote {OUTPUT} ({len(PAGES)} pages)")


if __name__ == "__main__":
    main()
