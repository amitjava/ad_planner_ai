"""PDF Report Generator"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from typing import Dict, Any
from ..models import FullPlanOutput
import os
import requests
from io import BytesIO


class PDFGenerator:
    """Generates PDF reports for marketing plans"""

    def __init__(self, output_dir: str = "./exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12
        ))

        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10
        ))

        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            spaceBefore=6,
            spaceAfter=6
        ))

    def generate_report(self, plan: FullPlanOutput, filename: str = None) -> str:
        """Generate PDF report for a plan"""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"marketing_plan_{plan.session_id}_{timestamp}.pdf"

        filepath = os.path.join(self.output_dir, filename)

        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []

        # Title
        title = Paragraph(
            f"Marketing Plan Report",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Session info
        info_text = f"<b>Session ID:</b> {plan.session_id}<br/><b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Paragraph(info_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Persona Section
        story.append(Paragraph("Target Persona", self.styles['SectionHeader']))
        persona_text = f"""
<b>Name:</b> {plan.persona.name}<br/>
<b>Age Range:</b> {plan.persona.age_range}<br/>
<b>Interests:</b> {', '.join(plan.persona.interests)}<br/>
<b>Platforms:</b> {', '.join(plan.persona.platforms)}<br/>
<b>Creative Style:</b> {plan.persona.creative_style}<br/>
<b>Motivation:</b> {plan.persona.motivation}
"""
        story.append(Paragraph(persona_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Location Recommendation Section
        story.append(Paragraph("Recommended Target Radius", self.styles['SectionHeader']))
        location_text = f"""
<b>Your Selection:</b> {plan.location_recommendation.current_miles} miles<br/>
<b>Our Recommendation:</b> {plan.location_recommendation.suggested_miles} miles<br/>
<b>Business Category:</b> {plan.location_recommendation.business_type_category}<br/>
<b>Typical Customer Travel:</b> {plan.location_recommendation.typical_customer_travel}<br/><br/>
<b>Why This Radius?</b><br/>
{plan.location_recommendation.reasoning}
"""
        story.append(Paragraph(location_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("<b>Optimization Factors:</b>", self.styles['Normal']))
        for factor in plan.location_recommendation.optimization_factors:
            story.append(Paragraph(f"• {factor}", self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Competitor Insights
        story.append(Paragraph("Competitive Landscape", self.styles['SectionHeader']))
        story.append(Paragraph(f"<b>Market Insights:</b> {plan.competitor_snapshot.market_insights}", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(f"<b>Opportunities:</b>", self.styles['Normal']))
        for opp in plan.competitor_snapshot.opportunities:
            story.append(Paragraph(f"• {opp}", self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Media Plans
        story.append(PageBreak())
        story.append(Paragraph("Media Plan Scenarios", self.styles['SectionHeader']))

        for plan_type, media_plan in [
            ("Standard Plan", plan.scenarios.standard_plan),
            ("Aggressive Plan", plan.scenarios.aggressive_plan),
            ("Experimental Plan", plan.scenarios.experimental_plan)
        ]:
            story.append(Paragraph(f"<b>{plan_type}</b>", self.styles['Heading3']))
            story.append(Paragraph(
                f"Budget: ${media_plan.total_budget:,.2f} | Duration: {media_plan.duration_weeks} weeks",
                self.styles['Normal']
            ))
            story.append(Spacer(1, 0.1 * inch))

            # Channel table
            table_data = [[
                Paragraph("<b>Channel</b>", self.styles['SmallText']),
                Paragraph("<b>Budget %</b>", self.styles['SmallText']),
                Paragraph("<b>Amount</b>", self.styles['SmallText']),
                Paragraph("<b>Reasoning</b>", self.styles['SmallText'])
            ]]
            for channel in media_plan.channels:
                amount = media_plan.total_budget * channel.budget_share_percent / 100
                table_data.append([
                    Paragraph(channel.name, self.styles['SmallText']),
                    Paragraph(f"{channel.budget_share_percent}%", self.styles['SmallText']),
                    Paragraph(f"${amount:,.0f}", self.styles['SmallText']),
                    Paragraph(channel.reasoning, self.styles['SmallText'])
                ])

            table = Table(table_data, colWidths=[1.3*inch, 0.7*inch, 0.9*inch, 3.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 0.2 * inch))

        # Creative Assets
        story.append(PageBreak())
        story.append(Paragraph("Creative Assets", self.styles['SectionHeader']))

        story.append(Paragraph("<b>Campaign Ideas:</b>", self.styles['CustomBodyText']))
        for idea in plan.creatives.ideas:
            story.append(Paragraph(f"<b>• {idea.title}:</b> {idea.description}", self.styles['CustomBodyText']))

            # Add image if available
            if idea.image_url:
                try:
                    img = self._fetch_and_create_image(idea.image_url, max_width=4*inch)
                    if img:
                        story.append(Spacer(1, 0.1 * inch))
                        story.append(img)
                        # Add image credit
                        if idea.image_prompt:
                            story.append(Paragraph(
                                f"<i>Search: {idea.image_prompt}</i>",
                                self.styles['SmallText']
                            ))
                except Exception as e:
                    print(f"Error adding image to PDF: {e}")

            story.append(Spacer(1, 0.15 * inch))

        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph(f"<b>Slogans:</b>", self.styles['CustomBodyText']))
        for slogan in plan.creatives.slogans:
            story.append(Paragraph(f"• \"{slogan}\"", self.styles['CustomBodyText']))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph(f"<b>Ad Copy (Short):</b>", self.styles['CustomBodyText']))
        story.append(Paragraph(plan.creatives.short_ad_copy, self.styles['CustomBodyText']))
        story.append(Spacer(1, 0.15 * inch))

        story.append(Paragraph(f"<b>Ad Copy (Long):</b>", self.styles['CustomBodyText']))
        story.append(Paragraph(plan.creatives.long_ad_copy, self.styles['CustomBodyText']))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph(f"<b>Hashtags:</b> {' '.join(['#' + tag.lstrip('#') for tag in plan.creatives.hashtags])}", self.styles['CustomBodyText']))
        story.append(Spacer(1, 0.3 * inch))

        # Performance Predictions
        story.append(PageBreak())
        story.append(Paragraph("Performance Predictions", self.styles['SectionHeader']))

        perf_data = [[
            Paragraph("<b>Plan Type</b>", self.styles['SmallText']),
            Paragraph("<b>Reach</b>", self.styles['SmallText']),
            Paragraph("<b>Clicks</b>", self.styles['SmallText']),
            Paragraph("<b>CPC</b>", self.styles['SmallText']),
            Paragraph("<b>ROI</b>", self.styles['SmallText'])
        ]]
        for plan_type in ["standard", "aggressive", "experimental"]:
            perf = plan.performance.get(plan_type, {})
            perf_data.append([
                Paragraph(plan_type.capitalize(), self.styles['SmallText']),
                Paragraph(str(perf.get("reach", "N/A")), self.styles['SmallText']),
                Paragraph(str(perf.get("clicks", "N/A")), self.styles['SmallText']),
                Paragraph(str(perf.get("cpc_estimate", "N/A")), self.styles['SmallText']),
                Paragraph(str(perf.get("roi_range", "N/A")), self.styles['SmallText'])
            ])

        perf_table = Table(perf_data, colWidths=[1.2*inch, 1.5*inch, 1.3*inch, 1.2*inch, 1.5*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(perf_table)
        story.append(Spacer(1, 0.3 * inch))

        # Evaluation
        story.append(Paragraph("Plan Evaluation", self.styles['SectionHeader']))
        eval_score = plan.critic_evaluation.get('overall_score', 0)
        story.append(Paragraph(f"<b>Overall Quality Score:</b> {eval_score:.2f} / 1.00", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        if plan.critic_evaluation.get('strengths'):
            story.append(Paragraph("<b>Strengths:</b>", self.styles['Normal']))
            for strength in plan.critic_evaluation['strengths']:
                story.append(Paragraph(f"✓ {strength}", self.styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))

        if plan.critic_evaluation.get('recommendations'):
            story.append(Paragraph("<b>Recommendations:</b>", self.styles['Normal']))
            for rec in plan.critic_evaluation['recommendations']:
                story.append(Paragraph(f"→ {rec}", self.styles['Normal']))

        # Build PDF
        doc.build(story)

        return filepath

    def _fetch_and_create_image(self, image_url: str, max_width: float = 4*inch) -> Image:
        """
        Fetch image from URL and create ReportLab Image object

        Args:
            image_url: URL of the image
            max_width: Maximum width for the image

        Returns:
            ReportLab Image object or None if failed
        """
        try:
            # Fetch image data
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # Create image from bytes
            img_data = BytesIO(response.content)
            img = Image(img_data)

            # Scale image to fit max_width while maintaining aspect ratio
            aspect_ratio = img.imageHeight / img.imageWidth
            img.drawWidth = max_width
            img.drawHeight = max_width * aspect_ratio

            return img

        except Exception as e:
            print(f"Error fetching image from {image_url}: {e}")
            return None
