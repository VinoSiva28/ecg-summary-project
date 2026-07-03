from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # needed so matplotlib doesn't try to open a window
import io
from datetime import datetime

def fig_to_image(fig):
    buf = io.BytesIO()       # create an empty buffer in memory
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    buf.seek(0)              # go back to start of buffer
    return buf

def build_plots(even_time, voltage_array, filtered, peaks, rr, beat_times):
    # raw signal
    fig1, ax1 = plt.subplots(figsize=(8, 2.5))
    ax1.plot(even_time, voltage_array, lw=0.5)
    ax1.set_title('Raw ECG Signal')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('ADC counts')
    raw_buf = fig_to_image(fig1)
    plt.close(fig1)

    # filtered with peaks
    fig2, ax2 = plt.subplots(figsize=(8, 2.5))
    ax2.plot(even_time, filtered, lw=0.6, color='orange')
    ax2.plot(even_time[peaks], filtered[peaks], 'rv', ms=5, label='R-peaks')
    ax2.set_title('Filtered ECG with R-peaks')
    ax2.set_xlabel('Time (s)')
    ax2.legend()
    filtered_buf = fig_to_image(fig2)
    plt.close(fig2)

    # RR intervals
    fig3, ax3 = plt.subplots(figsize=(8, 2.5))
    ax3.plot(beat_times, rr * 1000, marker='o', lw=1.2, color='mediumpurple')
    ax3.set_title('RR Intervals over time')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('RR (ms)')
    rr_buf = fig_to_image(fig3)
    plt.close(fig3)

    return raw_buf, filtered_buf, rr_buf
def generate_pdf(even_time, voltage_array, filtered, peaks, rr, 
                 bpm_per_beat, beat_times, irregular_intervals, snr, quality):

    buf = io.BytesIO()  # PDF goes into memory, not a file
    doc = SimpleDocTemplate(buf, pagesize=A4, 
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    story = []  # list of elements that get built into the PDF

    # title
    story.append(Paragraph("ECG Analysis Report", styles['Title']))
    story.append(Spacer(1, 0.2*inch))

    # recording info
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph(f"Recording Length: {even_time[-1]:.1f} seconds", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # metrics table
    story.append(Paragraph("Heart Rate Summary", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    table_data = [
        ['Metric', 'Value'],
        ['Average BPM', f"{bpm_per_beat.mean():.0f}"],
        ['Minimum BPM', f"{bpm_per_beat.min():.0f}"],
        ['Maximum BPM', f"{bpm_per_beat.max():.0f}"],
        ['Beats Detected', str(len(peaks))],
        ['Irregular Intervals', str(len(irregular_intervals))],
        ['Signal Quality', quality],
        ['SNR', f"{snr:.2f}"],
    ]
    
    table = Table(table_data, colWidths=[3*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.lightgrey]),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))

    # plots
    raw_buf, filtered_buf, rr_buf = build_plots(
        even_time, voltage_array, filtered, peaks, rr, beat_times)

    story.append(Paragraph("Raw ECG Signal", styles['Heading2']))
    story.append(Image(raw_buf, width=6.5*inch, height=2*inch))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Filtered ECG with R-peaks", styles['Heading2']))
    story.append(Image(filtered_buf, width=6.5*inch, height=2*inch))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("RR Intervals", styles['Heading2']))
    story.append(Image(rr_buf, width=6.5*inch, height=2*inch))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph(
        "Disclaimer: This report is generated for educational purposes only and does not constitute medical advice or diagnosis. Consult a qualified healthcare professional for any medical concerns.",
        styles['Italic']
    ))
    doc.build(story)
    buf.seek(0)
    return buf
