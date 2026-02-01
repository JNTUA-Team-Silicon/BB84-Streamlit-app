#!/usr/bin/env python3
"""
Comprehensive BB84 Learning Guide PDF
Contains all questions asked, answers, and mathematical formulas
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

def create_learning_guide():
    """Create comprehensive BB84 learning guide with Q&A and formulas"""
    
    # Create PDF
    filename = "BB84_Complete_Learning_Guide.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#0891b2'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    
    # Title Page
    story.append(Paragraph("BB84 Quantum Key Distribution", title_style))
    story.append(Paragraph("Complete Learning Guide", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", normal_style))
    story.append(Paragraph("JNTUA ECE Department | Team Silicon", normal_style))
    story.append(PageBreak())
    
    # Table of Contents
    story.append(Paragraph("Table of Contents", heading_style))
    toc_items = [
        "1. Questions Asked & Answers",
        "2. Mathematical Formulas & Equations",
        "3. Key Concepts Explained",
        "4. Practical Implementation Details"
    ]
    for item in toc_items:
        story.append(Paragraph(item, normal_style))
    story.append(PageBreak())
    
    # ===== SECTION 1: Q&A =====
    story.append(Paragraph("1. Questions Asked & Comprehensive Answers", heading_style))
    
    # Q1
    story.append(Paragraph("Q1: Error Suppression & SessionInfo Initialization Issues", subheading_style))
    story.append(Paragraph("""
    <b>Problem:</b> Application showing "Bad message format" and "SessionInfo before it was initialized" errors.<br/><br/>
    
    <b>Solution:</b><br/>
    • Optimized error suppression to target only specific errors (SessionInfo, Bad message format)<br/>
    • Removed aggressive stderr/stdout filtering that caused performance issues<br/>
    • Implemented MinimalErrorFilter class for lightweight error handling<br/>
    • Maintained early session state initialization at module level<br/><br/>
    
    <b>Result:</b> Clean startup, no error messages, improved app performance.
    """, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Q2
    story.append(Paragraph("Q2: Transmitted Bits in Key Metrics Display", subheading_style))
    story.append(Paragraph("""
    <b>Question:</b> Can we show transmitted bits in the key metrics?<br/><br/>
    
    <b>Answer:</b> Yes! Added two new metrics:<br/>
    • <b>Transmitted Bits:</b> Total number of qubits Alice sent through the quantum channel<br/>
    • <b>Sift Rate (Success Rate):</b> Percentage of transmitted bits that were successfully sifted<br/><br/>
    
    <b>Expected Values:</b><br/>
    • Normal: ~50% success rate (expected in BB84 due to random basis matching)<br/>
    • With Eve: May decrease below 50% due to eavesdropping errors<br/><br/>
    
    <b>Formula:</b> Sift Rate = (Sifted Bits / Transmitted Bits) × 100%
    """, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Q3
    story.append(Paragraph("Q3: Sifted Key Rate for Both Scenarios", subheading_style))
    story.append(Paragraph("""
    <b>Question:</b> Add sifted key rate for both No Eve and With Eve scenarios.<br/><br/>
    
    <b>Implementation:</b><br/>
    • Calculate sifted key rate separately for each scenario<br/>
    • No Eve scenario: Shows baseline sifting efficiency (blue color #1e40af)<br/>
    • With Eve scenario: Shows reduced efficiency (red color #dc2626)<br/>
    • Allows direct comparison of Eve's impact<br/><br/>
    
    <b>Calculation:</b><br/>
    Sift_Rate_No_Eve = (No_Eve_Sifted_Count / Transmitted_Bits) × 100%<br/>
    Sift_Rate_With_Eve = (With_Eve_Sifted_Count / Transmitted_Bits) × 100%
    """, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Q4
    story.append(Paragraph("Q4: Eve's Impact on Sifted Key Rate", subheading_style))
    story.append(Paragraph("""
    <b>Question:</b> If Eve intercepts, does the sifted key decrease?<br/><br/>
    
    <b>Answer:</b> <b>YES!</b> Added three-column impact analysis:<br/>
    • <b>Eve's Impact on Sift Rate (%):</b> Percentage decrease in sifting efficiency<br/>
    • <b>Sifted Bits Lost to Eve:</b> Actual count of bits lost<br/>
    • <b>Eve Detection Status:</b> Red (DETECTED) if QBER > threshold, Green (UNDETECTED) otherwise<br/><br/>
    
    <b>Why Decrease Happens:</b><br/>
    1. Eve measures in wrong basis ~50% of the time<br/>
    2. Wrong-basis measurements alter quantum states<br/>
    3. Eve re-sends corrupted qubits to Bob<br/>
    4. Alice-Bob basis matching faces additional errors<br/>
    5. Fewer bits pass verification → Lower sift rate
    """, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Q5
    story.append(Paragraph("Q5: What is Success Rate?", subheading_style))
    story.append(Paragraph("""
    <b>Definition:</b> Percentage of transmitted bits that were successfully sifted (basis-matched).<br/><br/>
    
    <b>Why ~50% in BB84?</b><br/>
    • Alice randomly chooses basis (Z or X) for each qubit: 50/50 probability<br/>
    • Bob randomly measures in basis (Z or X): 50/50 probability<br/>
    • They match only when both choose same basis: ~50% of the time<br/>
    • This is NORMAL and EXPECTED in BB84 protocol<br/><br/>
    
    <b>With Eve:</b><br/>
    • Eve's eavesdropping may introduce errors<br/>
    • Extra errors cause additional mismatches<br/>
    • Success rate may drop below 50%<br/>
    • Decrease reveals Eve's presence through QBER increase
    """, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Q6
    story.append(Paragraph("Q6: Color Legend for Metrics", subheading_style))
    story.append(Paragraph("""
    <b>Question:</b> Add color guide/legend for transmitted bits and success rate.<br/><br/>
    
    <b>Color Scheme:</b><br/>
    • <b>Cyan (#0891b2):</b> Transmitted bits, normal success rate<br/>
    • <b>Blue (#1e40af):</b> No Eve scenario metrics<br/>
    • <b>Red (#dc2626):</b> With Eve scenario, eavesdropping detected<br/>
    • <b>Orange (#f59e0b):</b> Eve's impact percentage<br/>
    • <b>Green (#16a34a):</b> Eve undetected (low QBER)<br/><br/>
    
    <b>Visual Legend:</b> Three colored boxes showing meaning of each color.
    """, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Q7
    story.append(Paragraph("Q7: How Sifted Bits Are Lost to Eve", subheading_style))
    story.append(Paragraph("""
    <b>Mechanism:</b><br/>
    1. Eve uses wrong basis: ~50% of Eve's choices don't match Alice's<br/>
    2. Wrong-basis measurement collapses quantum state incorrectly<br/>
    3. Eve re-sends incorrect state to Bob<br/>
    4. Bob's measurement gives wrong result for these bits<br/>
    5. During sifting, Alice & Bob find mismatches in their results<br/>
    6. These bits are rejected as "sifted bits lost"<br/><br/>
    
    <b>Mathematical View:</b><br/>
    Bits_Lost = Sifted_No_Eve - Sifted_With_Eve<br/>
    Impact_Rate = (Bits_Lost / Sifted_No_Eve) × 100%
    """, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Q8
    story.append(Paragraph("Q8: Why Sifted Bits Lost Shows Zero", subheading_style))
    story.append(Paragraph("""
    <b>Possible Reasons:</b><br/>
    1. <b>Low Eve Probability:</b> If Eve Probability ≤ 50%, Eve doesn't intercept all qubits<br/>
    2. <b>Statistical Variance:</b> Eve's random basis sometimes aligns correctly with Alice<br/>
    3. <b>Small Sample Size:</b> With limited transmitted bits, randomness dominates<br/><br/>
    
    <b>To See Bits Lost:</b><br/>
    • Increase Eve Probability slider to 80-100%<br/>
    • Increase Transmitted Bits to 500-2000<br/>
    • Run simulation multiple times (randomness matters)<br/>
    • Watch Eve's Impact Rate (%) instead of bit count
    """, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Q9
    story.append(Paragraph("Q9: Eve Detected Despite 0 Bits Lost", subheading_style))
    story.append(Paragraph("""
    <b>KEY INSIGHT: Eve is detected through QBER (error rate), NOT bit count!</b><br/><br/>
    
    <b>The Difference:</b><br/>
    • <b>Sifted Bits Lost:</b> Counts how many bits disappeared (quantity)<br/>
    • <b>QBER:</b> Measures error rate in remaining sifted bits (quality)<br/><br/>
    
    <b>Real Example:</b><br/>
    No Eve: 100 sifted bits, 0 errors → QBER = 0% ✅<br/>
    With Eve: 100 sifted bits, 15 errors → QBER = 15% ❌ DETECTED!<br/><br/>
    
    <b>Why?</b> Eve's wrong-basis measurements introduce BIT FLIPS in the remaining sifted bits!<br/>
    These errors show up as QBER exceeding the threshold (typically 11%).
    """, normal_style))
    story.append(PageBreak())
    
    # ===== SECTION 2: MATHEMATICAL FORMULAS =====
    story.append(Paragraph("2. Mathematical Formulas & Equations", heading_style))
    
    # BB84 Protocol Formulas
    story.append(Paragraph("BB84 Protocol Mathematics", subheading_style))
    
    formulas = [
        ("Sift Rate (Success Rate)", "Sift_Rate = (Sifted_Bits / Transmitted_Bits) × 100%", 
         "Percentage of transmitted bits where Alice and Bob used same basis"),
        
        ("Expected Sift Rate (No Eve)", "Sift_Rate_Expected = 50%", 
         "Since each person randomly chooses basis independently"),
        
        ("Sifted Key Rate", "Sifted_Rate = (Sifted_Count / Total_Transmitted) × 100%", 
         "Shows efficiency for each scenario (No Eve vs With Eve)"),
        
        ("Eve's Impact on Sifting", "Impact = Sift_Rate_NoEve - Sift_Rate_WithEve", 
         "Percentage point difference showing eavesdropping effect"),
        
        ("Bits Lost to Eve", "Bits_Lost = Sifted_Count_NoEve - Sifted_Count_WithEve", 
         "Absolute count of sifted bits lost due to eavesdropping"),
    ]
    
    for title, formula, desc in formulas:
        story.append(Paragraph(f"<b>{title}:</b>", subheading_style))
        story.append(Paragraph(formula, 
                              ParagraphStyle('Formula', parent=styles['Normal'], 
                                           fontName='Courier', fontSize=10, 
                                           textColor=colors.HexColor('#1e40af'))))
        story.append(Paragraph(f"<i>{desc}</i>", normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # QBER Formulas
    story.append(Paragraph("QBER (Quantum Bit Error Rate) Formulas", subheading_style))
    
    story.append(Paragraph("""
    <b>Basic QBER Calculation:</b><br/>
    QBER = (Number_of_Errors / Total_Sifted_Bits) × 100%<br/><br/>
    
    <b>Interpretation:</b><br/>
    • QBER = 0-3%: Low errors (no eavesdropper detected) ✅<br/>
    • QBER = 3-11%: Medium errors (depends on threshold setting)<br/>
    • QBER > 11%: High errors (eavesdropping DETECTED) ❌<br/><br/>
    
    <b>Theoretical QBER with Eve (Intercept-Resend):</b><br/>
    QBER_theoretical = 0.25 (25%) for Intercept-Resend attack<br/>
    • Eve guesses wrong basis 50% of the time<br/>
    • Wrong guess causes measurement error 50% of time<br/>
    • Total: 0.5 × 0.5 = 0.25 = 25%<br/><br/>
    
    <b>Detection Threshold:</b><br/>
    If QBER > Threshold → Eavesdropping Detected<br/>
    If QBER ≤ Threshold → Key is considered Secure ✅
    """, normal_style))
    
    story.append(Spacer(1, 0.15*inch))
    story.append(PageBreak())
    
    # Key Rate Formulas
    story.append(Paragraph("Key Rate & Privacy Amplification", subheading_style))
    
    story.append(Paragraph("""
    <b>Key Rate (Efficiency):</b><br/>
    Key_Rate = (Final_Key_Length / Transmitted_Bits)<br/>
    Example: 25 bits final key / 200 transmitted = 0.125 = 12.5% efficiency<br/><br/>
    
    <b>Final Secure Key Length:</b><br/>
    Final_Key = Privacy_Amplification(Sifted_Key, QBER)<br/><br/>
    
    <b>Shannon Entropy (Eve's Information):</b><br/>
    H(E) = -e·log₂(e) - (1-e)·log₂(1-e)<br/>
    where e = QBER<br/>
    (Gives maximum information Eve could have learned)<br/><br/>
    
    <b>Information-Theoretic Security:</b><br/>
    If QBER < threshold:<br/>
    Remaining_Eve_Info = 2^(-128) (exponentially small)<br/>
    Final key is cryptographically secure
    """, normal_style))
    
    story.append(Spacer(1, 0.15*inch))
    story.append(PageBreak())
    
    # Quantum State Formulas
    story.append(Paragraph("Quantum State Mathematics", subheading_style))
    
    story.append(Paragraph("""
    <b>Z-Basis (Rectilinear) States:</b><br/>
    |0⟩_Z = |0⟩ (vertical polarization)<br/>
    |1⟩_Z = |1⟩ (horizontal polarization)<br/><br/>
    
    <b>X-Basis (Diagonal) States:</b><br/>
    |0⟩_X = |+⟩ = (|0⟩ + |1⟩)/√2 (45° polarization)<br/>
    |1⟩_X = |-⟩ = (|0⟩ - |1⟩)/√2 (135° polarization)<br/><br/>
    
    <b>Measurement Probability:</b><br/>
    If prepared in Z-basis but measured in X-basis:<br/>
    P(correct) = |⟨+|0⟩|² = (1/√2)² = 0.5 = 50%<br/>
    P(incorrect) = |⟨-|0⟩|² = (1/√2)² = 0.5 = 50%<br/><br/>
    
    <b>This is why Eve introduces errors!</b> Wrong basis measurement gives random result.
    """, normal_style))
    
    story.append(Spacer(1, 0.15*inch))
    story.append(PageBreak())
    
    # Bloch Sphere Formulas
    story.append(Paragraph("Bloch Sphere Representation", subheading_style))
    
    story.append(Paragraph("""
    <b>General Qubit State:</b><br/>
    |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)·sin(θ/2)|1⟩<br/><br/>
    
    <b>Bloch Vector Coordinates:</b><br/>
    x = sin(θ)·cos(φ)<br/>
    y = sin(θ)·sin(φ)<br/>
    z = cos(θ)<br/><br/>
    
    <b>θ (Polar Angle):</b> θ = 2·arccos(|⟨0|ψ⟩|)<br/>
    <b>φ (Azimuthal Angle):</b> φ = arg(⟨1|ψ⟩) - arg(⟨0|ψ⟩)<br/><br/>
    
    <b>Basis States on Bloch Sphere:</b><br/>
    |0⟩ → (0, 0, 1) - North pole (Z-basis)<br/>
    |1⟩ → (0, 0, -1) - South pole (Z-basis)<br/>
    |+⟩ → (1, 0, 0) - +X axis (X-basis)<br/>
    |-⟩ → (-1, 0, 0) - -X axis (X-basis)
    """, normal_style))
    
    story.append(PageBreak())
    
    # ===== SECTION 3: KEY CONCEPTS =====
    story.append(Paragraph("3. Key Concepts Explained", heading_style))
    
    concepts = [
        ("Basis Matching", 
         "When Alice's basis equals Bob's basis for a particular qubit. Essential for BB84 sifting."),
        
        ("Sifting", 
         "Process of keeping only bits where Alice and Bob used the same measurement basis."),
        
        ("Eavesdropping Detection",
         "Detected through QBER (error rate), not through missing bits. Eve's measurements introduce errors."),
        
        ("Quantum Measurement",
         "Collapses superposition to definite state. Measuring in wrong basis gives random result."),
        
        ("Quantum Uncertainty",
         "Cannot know arbitrary observable of quantum state without destroying it (Heisenberg principle)."),
        
        ("Information-Theoretic Security",
         "Security guaranteed by laws of physics, not computational complexity. Eve gains negligible information."),
    ]
    
    for concept, explanation in concepts:
        story.append(Paragraph(f"<b>{concept}:</b> {explanation}", normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(PageBreak())
    
    # ===== SECTION 4: PRACTICAL DETAILS =====
    story.append(Paragraph("4. Practical Implementation Details", heading_style))
    
    story.append(Paragraph("Simulation Parameters", subheading_style))
    story.append(Paragraph("""
    <b>Transmitted Bits (qubits):</b> 50-2000 (configurable)<br/>
    Range determines sample size for statistical analysis.<br/><br/>
    
    <b>Eve Probability:</b> 0-100%<br/>
    Likelihood of Eve intercepting each qubit (0% = no eavesdropping, 100% = intercepts all).<br/><br/>
    
    <b>QBER Threshold:</b> Default 11%<br/>
    If QBER exceeds this, eavesdropping is detected and key rejected.<br/><br/>
    
    <b>Channel Noise:</b> Default 1%<br/>
    Environmental noise causing random bit flips (independent of Eve).<br/><br/>
    
    <b>Eve Attack Type:</b> Intercept-Resend (default)<br/>
    Eve measures and re-transmits, introducing detectable errors.
    """, normal_style))
    
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Metrics Explained", subheading_style))
    
    metrics_data = [
        ["Metric", "Formula", "Meaning"],
        ["Transmitted", "num_bits", "Total qubits sent"],
        ["Sift Rate", "(sifted/transmitted)×100%", "Success in basis matching"],
        ["Sifted Bits", "count where basis match", "Usable bits for key"],
        ["Errors", "sifted_bits - correct_bits", "Mismatches in sifted bits"],
        ["QBER", "(errors/sifted)×100%", "Error rate indicator"],
        ["Final Key", "privacy_amplify(sifted)", "Cryptographically secure key"],
        ["Key Rate", "final_key/transmitted", "Protocol efficiency"],
    ]
    
    tbl = Table(metrics_data, colWidths=[1.5*inch, 2.0*inch, 2.5*inch])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e7ff')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(tbl)
    
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Paragraph("=" * 80, normal_style))
    story.append(Paragraph("End of Learning Guide", 
                          ParagraphStyle('Footer', parent=styles['Normal'], 
                                       alignment=TA_CENTER, fontSize=10)))
    
    # Build PDF
    doc.build(story)
    print(f"\n✅ PDF Generated: {filename}")
    print(f"📁 Location: /home/keerthan/Desktop/bb84_2/{filename}")
    return filename

if __name__ == "__main__":
    create_learning_guide()
