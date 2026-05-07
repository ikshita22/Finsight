from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime


def generate_report(df, pl, bs, variance_df, filename="data/finsight_report.pdf"):

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontSize=20,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2C3E50"),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.grey,
        spaceAfter=12,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Normal"],
        fontSize=13,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2C3E50"),
        spaceBefore=16,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica",
        textColor=colors.HexColor("#2C3E50"),
        spaceAfter=6
    )

    elements = []

    # ─── TITLE ─────────────────────────────────────────────────────
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("FinSight — Financial Intelligence Report", title_style))
    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%d %B %Y, %H:%M:%S')}",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2C3E50")))
    elements.append(Spacer(1, 0.15 * inch))

    # ─── EXECUTIVE SUMMARY ─────────────────────────────────────────
    elements.append(Paragraph("Executive Summary", heading_style))

    total_transactions = len(df)
    total_anomalies = int(df["any_anomaly"].sum())
    net_income = pl["Net Income"]
    balance_status = bs["Balance Check"]

    summary_text = (
        f"This report covers <b>{total_transactions:,}</b> financial transactions analysed by the "
        f"FinSight intelligence pipeline. A total of <b>{total_anomalies}</b> anomalies were detected "
        f"across rule-based, statistical, and machine learning detection layers. "
        f"The firm recorded a net income of <b>${net_income:,.2f}</b> for the reporting period. "
        f"Balance sheet validation status: <b>{balance_status}</b>."
    )
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 0.1 * inch))

    # ─── P&L STATEMENT ─────────────────────────────────────────────
    elements.append(Paragraph("P&L Statement", heading_style))

    pl_data = [["Metric", "Value"]]
    for k, v in pl.items():
        if isinstance(v, float):
            pl_data.append([k, f"${v:,.2f}"])
        else:
            pl_data.append([k, str(v)])

    pl_table = Table(pl_data, colWidths=[3 * inch, 3 * inch])
    pl_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F3F4")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(pl_table)

    # ─── BALANCE SHEET ─────────────────────────────────────────────
    elements.append(Paragraph("Balance Sheet", heading_style))

    bs_data = [["Metric", "Value"]]
    for k, v in bs.items():
        if isinstance(v, float):
            bs_data.append([k, f"${v:,.2f}"])
        else:
            bs_data.append([k, str(v)])

    bs_table = Table(bs_data, colWidths=[3 * inch, 3 * inch])

    bs_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F3F4")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]

    # color balance check row
    for i, (k, v) in enumerate(bs.items()):
        if k == "Balance Check":
            row_idx = i + 1
            if v == "BALANCED":
                bs_style.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#D5F5E3")))
            else:
                bs_style.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#FADBD8")))

    bs_table.setStyle(TableStyle(bs_style))
    elements.append(bs_table)

    # ─── VARIANCE ANALYSIS ─────────────────────────────────────────
    elements.append(Paragraph("Variance Analysis", heading_style))

    var_data = [["Account Type", "Actual", "Budget", "Variance", "Variance %"]]
    for _, row in variance_df.iterrows():
        var_data.append([
            row["account_type"],
            f"${row['actual']:,.2f}",
            f"${row['budget']:,.2f}",
            f"${row['variance']:,.2f}",
            f"{row['variance_pct']}%"
        ])

    var_table = Table(var_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1*inch])

    var_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]

    for i, (_, row) in enumerate(variance_df.iterrows()):
        row_idx = i + 1
        if row["variance_pct"] > 0:
            var_style.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#FADBD8")))
        else:
            var_style.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#D5F5E3")))

    var_table.setStyle(TableStyle(var_style))
    elements.append(var_table)

    # ─── TOP 15 ANOMALIES ──────────────────────────────────────────
    elements.append(Paragraph("Top 15 Anomalous Transactions", heading_style))

    anomalies = df[df["any_anomaly"] == True].sort_values("debit", ascending=False).head(15)

    anom_data = [["Transaction ID", "Date", "Account Type", "Debit", "Credit", "Flag Reason"]]
    for _, row in anomalies.iterrows():
        anom_data.append([
            str(row["transaction_id"]),
            str(row["date"]),
            str(row["account_type"]),
            f"${row['debit']:,.2f}",
            f"${row['credit']:,.2f}",
            str(row["flag_reason"]) if row["flag_reason"] else "ML/Z-Score"
        ])

    anom_table = Table(
        anom_data,
        colWidths=[1.2*inch, 0.9*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.6*inch]
    )
    anom_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F3F4")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("ALIGN", (3, 0), (4, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(anom_table)

    # ─── BUILD ─────────────────────────────────────────────────────
    doc.build(elements)
    print(f"[✓] Report saved to {filename}")