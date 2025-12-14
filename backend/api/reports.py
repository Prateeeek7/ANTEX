"""
Comprehensive PDF Report Generation for Antenna Designs.

Generates professional design reports with ALL project data:
- Project specifications
- Optimization runs history
- Design candidates
- Simulation results
- RF Analysis (Smith Chart, impedance matching)
- Performance metrics
- Recommendations
"""
from typing import Dict, Any, Optional, List
import logging
import io
import base64
from datetime import datetime

logger = logging.getLogger(__name__)


def _generate_ai_recommendations(
    project_data: Dict[str, Any],
    best_design: Optional[Dict[str, Any]],
    performance_metrics: Optional[Dict[str, Any]],
    rf_analysis: Optional[Dict[str, Any]],
    optimization_runs: List[Dict[str, Any]]
) -> List[str]:
    """
    Generate AI-powered design recommendations based on analysis results.
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    if not best_design or not performance_metrics:
        recommendations.append("🚀 **Next Steps**: Run an optimization to generate design candidates and recommendations.")
        return recommendations
    
    metrics = best_design.get('candidate', {}).get('metrics', {})
    fitness = best_design.get('candidate', {}).get('fitness', 0)
    
    # Fitness-based recommendations
    if fitness > 0.8:
        recommendations.append("✅ **Excellent Design**: Your antenna design shows excellent performance. Consider fine-tuning for even better results.")
    elif fitness > 0.6:
        recommendations.append("👍 **Good Design**: The design meets basic requirements. Consider optimizing substrate properties or feed position for better performance.")
    else:
        recommendations.append("⚠️ **Needs Improvement**: The design needs optimization. Consider adjusting geometry parameters or using a different shape family.")
    
    # Frequency accuracy recommendations
    freq_error = performance_metrics.get('frequency_error_percent', 100)
    target_freq = project_data.get('target_frequency_ghz', 0)
    if freq_error < 3:
        recommendations.append(f"✅ **Frequency Accuracy**: Excellent frequency accuracy ({freq_error:.2f}% error). Design resonates very close to target {target_freq:.2f} GHz.")
    elif freq_error < 5:
        recommendations.append(f"ℹ️ **Frequency Tuning**: Good frequency accuracy ({freq_error:.2f}% error). Minor adjustments to patch dimensions could improve accuracy.")
    else:
        recommendations.append(f"⚠️ **Frequency Adjustment Needed**: Frequency error is {freq_error:.2f}%. Consider adjusting patch length/width to shift resonant frequency toward {target_freq:.2f} GHz.")
    
    # Gain recommendations
    gain = metrics.get('gain_estimate_dBi', 0)
    target_gain = project_data.get('target_gain_dbi', 0)
    if target_gain > 0:
        if gain >= target_gain:
            recommendations.append(f"✅ **Gain Target Met**: Gain of {gain:.2f} dBi meets target of {target_gain:.2f} dBi.")
        else:
            recommendations.append(f"📈 **Increase Gain**: Current gain is {gain:.2f} dBi (target: {target_gain:.2f} dBi). Consider: thicker substrate, larger patch area, or optimized feed position.")
    
    # Impedance matching recommendations
    if rf_analysis:
        vswr = rf_analysis.get('vswr', 0)
        matched = rf_analysis.get('matched', False)
        if matched:
            recommendations.append("✅ **Impedance Matching**: Excellent impedance match (VSWR < 2.0). No matching network required.")
        elif vswr > 3.0:
            recommendations.append("⚠️ **Impedance Matching Critical**: High VSWR indicates significant mismatch. Strongly recommend implementing a matching network (see RF Analysis section).")
        elif vswr > 2.0:
            recommendations.append("ℹ️ **Impedance Matching Recommended**: Moderate VSWR. A matching network can improve performance and reduce reflections.")
    
    # Bandwidth recommendations
    bandwidth = metrics.get('estimated_bandwidth_mhz', 0)
    target_bw = project_data.get('bandwidth_mhz', 0)
    if target_bw > 0:
        if bandwidth >= target_bw * 0.9:
            recommendations.append(f"✅ **Bandwidth Target Met**: Bandwidth of {bandwidth:.1f} MHz meets target requirements.")
        else:
            recommendations.append(f"📊 **Increase Bandwidth**: Current bandwidth is {bandwidth:.1f} MHz (target: {target_bw:.1f} MHz). Consider: thicker substrate, lower dielectric constant, or parasitic patches.")
    
    # Shape-specific recommendations
    geometry = best_design.get('candidate', {}).get('geometry_params', {})
    shape_family = geometry.get('shape_family', 'rectangular_patch')
    if shape_family == 'star_patch':
        recommendations.append("⭐ **Star Patch Design**: Star-shaped patches can provide better bandwidth and circular polarization. Verify feed position is optimized for this geometry.")
    elif shape_family == 'meandered_line':
        recommendations.append("📐 **Meandered Line Design**: Compact design with reduced size. Ensure meander parameters are optimized for your target frequency.")
    
    # Substrate recommendations
    substrate = project_data.get('substrate', 'FR4')
    if substrate == 'FR4':
        recommendations.append("📋 **Substrate Note**: FR4 is cost-effective but has higher loss. For better performance, consider Rogers 5880 or similar low-loss substrates.")
    elif substrate in ['Rogers 5880', 'Rogers RO5880']:
        recommendations.append("✅ **Substrate Choice**: Rogers 5880 provides excellent low-loss performance. Good choice for high-performance applications.")
    
    # Optimization algorithm recommendations
    if optimization_runs:
        latest_run = optimization_runs[0] if optimization_runs else {}
        algo = latest_run.get('algorithm', '')
        if algo == 'ga' and len(optimization_runs) > 1:
            recommendations.append("🧬 **GA Optimization**: Genetic Algorithm found good solutions. Consider running more generations for fine-tuning.")
        elif algo == 'pso':
            recommendations.append("🐦 **PSO Optimization**: Particle Swarm Optimization converged. Try GA algorithm for comparison if results need improvement.")
    
    return recommendations

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab not available. PDF reports will be limited.")


def generate_comprehensive_project_report(
    project_data: Dict[str, Any],
    optimization_runs: List[Dict[str, Any]],
    design_candidates: List[Dict[str, Any]],
    best_design: Optional[Dict[str, Any]],
    simulation_results: Optional[Dict[str, Any]],
    rf_analysis: Optional[Dict[str, Any]],
    performance_metrics: Optional[Dict[str, Any]]
) -> bytes:
    """
    Generate comprehensive PDF report with ALL project findings.
    
    Args:
        project_data: Project information
        optimization_runs: List of all optimization runs
        design_candidates: List of design candidates
        best_design: Best design candidate data
        simulation_results: Simulation results (Meep/FDTD)
        rf_analysis: RF analysis data (impedance, Smith chart)
        performance_metrics: Performance metrics data
        
    Returns:
        PDF file as bytes
    """
    if not REPORTLAB_AVAILABLE:
        return _generate_text_report_comprehensive(
            project_data, optimization_runs, design_candidates, best_design,
            simulation_results, rf_analysis, performance_metrics
        )
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#3a606e'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#607b7d'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#828e82'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Title Page - Clean Markdown Style
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("Comprehensive Antenna Design Report", title_style))
    story.append(Spacer(1, 0.4*inch))
    
    # Project Name - as H2
    story.append(Paragraph(project_data.get('name', 'Unnamed Project'), heading_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Report metadata - subtle
    body_style = styles['Normal']
    metadata_style = ParagraphStyle(
        'Metadata',
        parent=body_style,
        fontSize=9,
        textColor=colors.HexColor('#718096'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", metadata_style))
    story.append(PageBreak())
    
    # 1. PROJECT INFORMATION - Markdown-style section
    story.append(Paragraph("## Project Information", heading_style))
    
    # Clean key-value pairs in markdown table style
    project_details = [
        ['**Project Name:**', project_data.get('name', 'N/A')],
        ['**Description:**', project_data.get('description', 'N/A') or 'No description'],
        ['**Target Frequency:**', f"{project_data.get('target_frequency_ghz', 0):.3f} GHz"],
        ['**Target Bandwidth:**', f"{project_data.get('bandwidth_mhz', 0):.1f} MHz"],
        ['**Maximum Size:**', f"{project_data.get('max_size_mm', 0):.1f} mm"],
        ['**Substrate Material:**', project_data.get('substrate', 'N/A')],
        ['**Project Status:**', project_data.get('status', 'N/A').upper()],
        ['**Created:**', datetime.fromisoformat(str(project_data.get('created_at', ''))).strftime('%B %d, %Y') if project_data.get('created_at') else 'N/A']
    ]
    
    # Clean, minimal table style
    project_table = Table(project_details, colWidths=[2.2 * inch, 4.8 * inch])
    project_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2d3748')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#4a5568')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
    ]))
    story.append(project_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # 2. OPTIMIZATION RUNS
    story.append(Paragraph("2. Optimization Runs History", heading_style))
    if optimization_runs:
        for idx, run in enumerate(optimization_runs[:10], 1):  # Limit to first 10 runs
            story.append(Paragraph(f"Run #{run.get('id', idx)}", subheading_style))
            run_info = [
                ['Algorithm:', run.get('algorithm', 'N/A').upper()],
                ['Status:', run.get('status', 'N/A').upper()],
                ['Population Size:', str(run.get('population_size', 'N/A'))],
                ['Generations:', str(run.get('generations', 'N/A'))],
                ['Best Fitness:', f"{run.get('best_fitness', 0):.4f}" if run.get('best_fitness') else 'N/A'],
                ['Created:', datetime.fromisoformat(str(run.get('created_at', ''))).strftime('%Y-%m-%d %H:%M') if run.get('created_at') else 'N/A']
            ]
            run_table = Table(run_info, colWidths=[2 * inch, 5 * inch])
            run_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#aaae8e')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#828e82')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9faf9')])
            ]))
            story.append(run_table)
            story.append(Spacer(1, 0.2 * inch))
        
        if len(optimization_runs) > 10:
            story.append(Paragraph(f"... and {len(optimization_runs) - 10} more runs", styles['Normal']))
    else:
        story.append(Paragraph("No optimization runs have been executed yet.", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    # 3. DESIGN CANDIDATES
    story.append(Paragraph("3. Design Candidates", heading_style))
    if design_candidates:
        story.append(Paragraph(f"Total Candidates: {len(design_candidates)}", subheading_style))
        
        # Best candidate first - Enhanced display
        if best_design:
            story.append(Paragraph("🏆 Best Design Candidate", subheading_style))
            story.append(Spacer(1, 0.15 * inch))
            best_candidate = best_design.get('candidate', {})
            geometry = best_candidate.get('geometry_params', {})
            metrics = best_candidate.get('metrics', {})
            
            # Geometry parameters table
            best_info = [
                ['Fitness Score:', f"{best_candidate.get('fitness', 0):.4f}"],
                ['Shape Family:', str(geometry.get('shape_family', 'N/A')).replace('_', ' ').title()],
            ]
            
            # Add key geometry parameters
            geom_keys = [k for k in geometry.keys() if isinstance(geometry.get(k), (int, float)) and k not in ['shape_family', 'design_type']][:6]
            for key in geom_keys:
                value = geometry.get(key)
                best_info.append([key.replace('_', ' ').title() + ':', f"{value:.3f}"])
            
            best_table = Table(best_info, colWidths=[2.5 * inch, 4.5 * inch])
            best_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#607b7d')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#828e82')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9faf9')])
            ]))
            story.append(best_table)
            
            # Performance metrics table
            if metrics:
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph("Performance Metrics:", subheading_style))
                perf_info = []
                if metrics.get('estimated_freq_ghz') is not None:
                    perf_info.append(['Resonant Frequency:', f"{metrics.get('estimated_freq_ghz', 0):.3f} GHz"])
                if metrics.get('return_loss_dB') is not None:
                    perf_info.append(['Return Loss:', f"{metrics.get('return_loss_dB', 0):.2f} dB"])
                if metrics.get('gain_estimate_dBi') is not None:
                    perf_info.append(['Gain:', f"{metrics.get('gain_estimate_dBi', 0):.2f} dBi"])
                if metrics.get('vswr') is not None:
                    perf_info.append(['VSWR:', f"{metrics.get('vswr', 0):.2f}"])
                if metrics.get('estimated_bandwidth_mhz') is not None:
                    perf_info.append(['Bandwidth:', f"{metrics.get('estimated_bandwidth_mhz', 0):.1f} MHz"])
                
                if perf_info:
                    perf_table = Table(perf_info, colWidths=[2.5 * inch, 4.5 * inch])
                    perf_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#3a606e')),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#828e82')),
                        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.white, colors.HexColor('#f9faf9')])
                    ]))
                    story.append(perf_table)
            
            story.append(Spacer(1, 0.3 * inch))
        
        # Top candidates summary
        story.append(Paragraph(f"Top {min(5, len(design_candidates))} Candidates Summary", subheading_style))
        top_candidates = sorted(design_candidates, key=lambda x: x.get('fitness', 0), reverse=True)[:5]
        candidate_summary = [['Rank', 'Fitness', 'Return Loss (dB)', 'Gain (dBi)', 'Shape Family']]
        
        for idx, candidate in enumerate(top_candidates, 1):
            metrics = candidate.get('metrics', {})
            geometry = candidate.get('geometry_params', {})
            candidate_summary.append([
                f"#{idx}",
                f"{candidate.get('fitness', 0):.3f}",
                f"{metrics.get('return_loss_dB', 0):.2f}" if metrics.get('return_loss_dB') else 'N/A',
                f"{metrics.get('gain_estimate_dBi', 0):.2f}" if metrics.get('gain_estimate_dBi') else 'N/A',
                str(geometry.get('shape_family', 'N/A')).replace('_', ' ').title()[:20]
            ])
        
        summary_table = Table(candidate_summary, colWidths=[0.5*inch, 1*inch, 1.2*inch, 1*inch, 3.3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3a606e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#828e82')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9faf9')])
        ]))
        story.append(summary_table)
    else:
        story.append(Paragraph("No design candidates have been generated yet.", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    story.append(PageBreak())
    
    # 4. SIMULATION RESULTS
    story.append(Paragraph("4. Simulation Results", heading_style))
    if simulation_results:
        sim_method = simulation_results.get('simulation_method', 'analytical')
        story.append(Paragraph(f"Simulation Method: {sim_method.replace('_', ' ').title()}", subheading_style))
        
        sim_metrics = simulation_results.get('metrics', {})
        if sim_metrics:
            sim_info = [
                ['Resonant Frequency:', f"{sim_metrics.get('resonant_frequency_ghz', sim_metrics.get('frequency_ghz', 0)):.3f} GHz"],
                ['Return Loss:', f"{sim_metrics.get('return_loss_dB', sim_metrics.get('s11_db', 0)):.2f} dB"],
                ['Bandwidth:', f"{sim_metrics.get('bandwidth_mhz', 0):.1f} MHz"],
                ['Gain:', f"{sim_metrics.get('gain_dbi', sim_metrics.get('gain_estimate_dBi', 0)):.2f} dBi"],
            ]
            
            sim_table = Table(sim_info, colWidths=[2.5 * inch, 4.5 * inch])
            sim_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#aaae8e')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#828e82')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9faf9')])
            ]))
            story.append(sim_table)
        
        if simulation_results.get('s11_data'):
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("S11 Data: Available (see interactive charts in web interface)", styles['Normal']))
    else:
        story.append(Paragraph("No simulation results available. Run a simulation to generate results.", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    # 5. RF ANALYSIS
    story.append(Paragraph("5. RF Analysis & Impedance Matching", heading_style))
    if rf_analysis:
        rf_info = [
            ['Impedance:', f"{rf_analysis.get('impedance_real', 0):.2f} + j{rf_analysis.get('impedance_imag', 0):.2f} Ω"],
            ['VSWR:', f"{rf_analysis.get('vswr', 0):.2f}"],
            ['Return Loss:', f"{rf_analysis.get('return_loss_db', 0):.2f} dB"],
            ['Match Status:', '✓ Matched' if rf_analysis.get('matched', False) else '✗ Needs Matching'],
        ]
        
        rf_table = Table(rf_info, colWidths=[2.5 * inch, 4.5 * inch])
        rf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#607b7d')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#828e82')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9faf9')])
        ]))
        story.append(rf_table)
        
        # AI Recommendations
        ai_recs = rf_analysis.get('ai_recommendations', {})
        if ai_recs:
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("AI Matching Recommendations:", subheading_style))
            if ai_recs.get('overall'):
                story.append(Paragraph(f"<b>Overall:</b> {ai_recs.get('overall')}", styles['Normal']))
            if ai_recs.get('best_practice'):
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph(f"<b>Best Practice:</b> {ai_recs.get('best_practice')}", styles['Normal']))
        
        # Matching Networks
        matching_networks = rf_analysis.get('matching_networks', [])
        if matching_networks:
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("Recommended Matching Networks:", subheading_style))
            for idx, network in enumerate(matching_networks[:3], 1):
                story.append(Paragraph(f"{idx}. {network.get('type', 'N/A')} Network", styles['Normal']))
                story.append(Paragraph(f"   {network.get('description', '')}", styles['Normal']))
    else:
        story.append(Paragraph("No RF analysis data available. Run impedance analysis to generate results.", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    story.append(PageBreak())
    
    # 6. PERFORMANCE METRICS
    story.append(Paragraph("6. Comprehensive Performance Metrics", heading_style))
    if performance_metrics:
        perf_info = [
            ['Overall Score:', f"{performance_metrics.get('overall_score', 0):.1f}/100"],
            ['Resonant Frequency:', f"{performance_metrics.get('resonant_frequency_ghz', 0):.3f} GHz"],
            ['Target Frequency:', f"{performance_metrics.get('target_frequency_ghz', 0):.3f} GHz"],
            ['Frequency Error:', f"{performance_metrics.get('frequency_error_percent', 0):.2f}%"],
            ['Bandwidth:', f"{performance_metrics.get('bandwidth_mhz', 0):.1f} MHz"],
            ['Target Bandwidth:', f"{performance_metrics.get('target_bandwidth_mhz', 0):.1f} MHz"],
            ['Gain:', f"{performance_metrics.get('gain_dbi', 0):.2f} dBi"],
            ['Directivity:', f"{performance_metrics.get('directivity_dbi', 0):.2f} dBi"],
            ['Efficiency:', f"{performance_metrics.get('efficiency_percent', 0):.1f}%"],
            ['VSWR:', f"{performance_metrics.get('vswr', 0):.2f}"],
            ['E-plane Beamwidth:', f"{performance_metrics.get('beamwidth_e_plane_deg', 0):.1f}°"],
            ['H-plane Beamwidth:', f"{performance_metrics.get('beamwidth_h_plane_deg', 0):.1f}°"],
        ]
        
        perf_table = Table(perf_info, colWidths=[2.5 * inch, 4.5 * inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#607b7d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 12),
            ('FONTSIZE', (1, 1), (1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#828e82')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9faf9')])
        ]))
        story.append(perf_table)
        
        # Score Breakdown
        score_breakdown = performance_metrics.get('score_breakdown', {})
        if score_breakdown:
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("Performance Score Breakdown:", subheading_style))
            score_data = [[k.replace('_', ' ').title(), f"{v:.1f}/100"] for k, v in score_breakdown.items()]
            score_table = Table(score_data, colWidths=[4 * inch, 3 * inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#aaae8e')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#828e82')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9faf9')])
            ]))
            story.append(score_table)
    else:
        story.append(Paragraph("No performance metrics available. Complete optimization and simulation to generate metrics.", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    # 7. AI RECOMMENDATIONS & INSIGHTS
    story.append(Paragraph("7. AI Recommendations & Design Insights", heading_style))
    story.append(Paragraph(
        "Our AI engine has analyzed your design results and provides the following intelligent recommendations:",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2 * inch))
    
    # Generate AI recommendations
    ai_recommendations = _generate_ai_recommendations(
        project_data, best_design, performance_metrics, rf_analysis, optimization_runs
    )
    
    if ai_recommendations:
        # Recommendation style with better formatting
        rec_style = ParagraphStyle(
            'Recommendation',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=0.2 * inch,
            spaceAfter=0.2 * inch,
            leading=14,
            bulletIndent=0.15 * inch
        )
        
        # Box style for recommendations
        rec_box_style = ParagraphStyle(
            'RecBox',
            parent=rec_style,
            backColor=colors.HexColor('#f0f7f7'),
            borderPadding=8,
            borderWidth=1,
            borderColor=colors.HexColor('#607b7d')
        )
        
        for rec in ai_recommendations:
            # Parse markdown-like formatting: convert **text** to <b>text</b>
            formatted_rec = rec
            # Handle bold markers
            import re
            formatted_rec = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_rec)
            story.append(Paragraph(formatted_rec, rec_style))
    else:
        story.append(Paragraph("Run optimization to generate AI-powered recommendations.", styles['Normal']))
    
    story.append(Spacer(1, 0.3 * inch))
    story.append(PageBreak())
    
    # 8. SUMMARY & KEY FINDINGS
    story.append(Paragraph("8. Summary & Key Findings", heading_style))
    summary_text = f"""
    This comprehensive report summarizes all design activities for the <b>{project_data.get('name', 'project')}</b> antenna design project.
    """
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))
    
    story.append(Paragraph("<b>Key Findings:</b>", subheading_style))
    findings = []
    if best_design:
        findings.append(f"• Best design candidate achieved fitness score of {best_design.get('candidate', {}).get('fitness', 0):.4f}")
    if performance_metrics:
        findings.append(f"• Overall performance score: {performance_metrics.get('overall_score', 0):.1f}/100")
        if performance_metrics.get('frequency_error_percent', 100) < 5:
            findings.append(f"• Excellent frequency accuracy: {performance_metrics.get('frequency_error_percent', 0):.2f}% error")
    if rf_analysis and rf_analysis.get('matched'):
        findings.append("• Impedance matching achieved - VSWR within acceptable range")
    elif rf_analysis:
        findings.append("• Impedance matching recommended - see RF Analysis section for matching networks")
    
    if not findings:
        findings.append("• Project is in early stages - complete optimization runs to generate findings")
    
    for finding in findings:
        story.append(Paragraph(finding, styles['Normal']))
    
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("<b>Next Steps:</b>", subheading_style))
    next_steps = [
        "1. Review design candidates and select optimal configuration",
        "2. Run FDTD simulation for industry-grade validation",
        "3. Analyze RF performance and impedance matching requirements",
        "4. Export geometry for fabrication (STL/DXF)",
        "5. Validate design in professional EM tools (HFSS/CST)"
    ]
    for step in next_steps:
        story.append(Paragraph(step, styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 0.5 * inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("Generated by ANTEX - Industry-Grade Antenna Design Tool", footer_style))
    story.append(Paragraph(f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))
    
    # Build PDF with error handling
    try:
        doc.build(story)
        pdf_bytes = buffer.getvalue()  # Use getvalue() for BytesIO
        
        # Verify PDF was generated correctly (check PDF magic bytes)
        if len(pdf_bytes) < 4 or pdf_bytes[:4] != b'%PDF':
            logger.error(f"Generated PDF does not have correct PDF header. First bytes: {pdf_bytes[:20]}")
            raise ValueError("PDF generation failed - invalid PDF structure")
        
        logger.info(f"PDF generated successfully: {len(pdf_bytes)} bytes")
        return pdf_bytes
    except Exception as e:
        logger.error(f"Error building PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise  # Re-raise to let the endpoint handle it


def generate_design_report(
    project_data: Dict[str, Any],
    design_data: Dict[str, Any],
    metrics_data: Dict[str, Any],
    radiation_data: Optional[Dict[str, Any]] = None
) -> bytes:
    """
    Generate PDF design report (legacy function for backward compatibility).
    """
    # Handle both old format (direct candidate data) and new format (with 'candidate' key)
    if 'candidate' in design_data:
        candidate_data = design_data['candidate']
        best_design = design_data
        candidates_list = [candidate_data]
    else:
        # Old format - wrap in 'candidate' structure
        candidate_data = design_data
        best_design = {'candidate': design_data}
        candidates_list = [design_data]
    
    return generate_comprehensive_project_report(
        project_data=project_data,
        optimization_runs=[],
        design_candidates=candidates_list,
        best_design=best_design,
        simulation_results=None,
        rf_analysis=None,
        performance_metrics=metrics_data
    )


def _generate_text_report_comprehensive(
    project_data: Dict[str, Any],
    optimization_runs: List[Dict[str, Any]],
    design_candidates: List[Dict[str, Any]],
    best_design: Optional[Dict[str, Any]],
    simulation_results: Optional[Dict[str, Any]],
    rf_analysis: Optional[Dict[str, Any]],
    performance_metrics: Optional[Dict[str, Any]]
) -> bytes:
    """Generate simple text report as fallback."""
    report = f"""
{'='*70}
COMPREHENSIVE ANTENNA DESIGN REPORT
{'='*70}

PROJECT INFORMATION
{'-'*70}
Project Name: {project_data.get('name', 'N/A')}
Target Frequency: {project_data.get('target_frequency_ghz', 0):.3f} GHz
Target Bandwidth: {project_data.get('bandwidth_mhz', 0):.1f} MHz
Substrate: {project_data.get('substrate', 'N/A')}

OPTIMIZATION RUNS
{'-'*70}
"""
    for run in optimization_runs[:10]:
        report += f"Run #{run.get('id')}: {run.get('algorithm', 'N/A').upper()} - {run.get('status', 'N/A').upper()} - Fitness: {run.get('best_fitness', 0):.4f}\n"
    
    report += f"""
DESIGN CANDIDATES
{'-'*70}
Total Candidates: {len(design_candidates)}
"""
    if best_design:
        report += f"Best Fitness: {best_design.get('candidate', {}).get('fitness', 0):.4f}\n"
    
    if simulation_results:
        report += f"""
SIMULATION RESULTS
{'-'*70}
Method: {simulation_results.get('simulation_method', 'analytical')}
"""
    
    if rf_analysis:
        report += f"""
RF ANALYSIS
{'-'*70}
Impedance: {rf_analysis.get('impedance_real', 0):.2f} + j{rf_analysis.get('impedance_imag', 0):.2f} Ω
VSWR: {rf_analysis.get('vswr', 0):.2f}
"""
    
    if performance_metrics:
        report += f"""
PERFORMANCE METRICS
{'-'*70}
Overall Score: {performance_metrics.get('overall_score', 0):.1f}/100
Resonant Frequency: {performance_metrics.get('resonant_frequency_ghz', 0):.3f} GHz
Gain: {performance_metrics.get('gain_dbi', 0):.2f} dBi
"""
    
    report += f"\n{'='*70}\nGenerated by ANTEX\n"
    return report.encode('utf-8')


def _generate_text_report(
    project_data: Dict[str, Any],
    design_data: Dict[str, Any],
    metrics_data: Dict[str, Any]
) -> bytes:
    """Generate simple text report as fallback (legacy)."""
    return _generate_text_report_comprehensive(
        project_data, [], [design_data] if design_data else [], design_data,
        None, None, metrics_data
    )
