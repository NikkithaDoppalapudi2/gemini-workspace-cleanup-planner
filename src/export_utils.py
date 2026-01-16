"""
Export Utilities Module
Handles CSV, Excel, and PDF export functionality
"""

import pandas as pd
from io import BytesIO
from datetime import datetime


def export_to_csv(df: pd.DataFrame) -> str:
    """Export dataframe to CSV string."""
    return df.to_csv(index=False)


def export_to_excel(df: pd.DataFrame, include_summary: bool = True) -> BytesIO:
    """
    Export dataframe to Excel with multiple sheets.
    
    Sheets:
    - Summary: Key statistics
    - All Users: Complete data
    - High Risk: Users with high/critical risk scores
    """
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: All Users
        df.to_excel(writer, sheet_name='All Users', index=False)
        
        # Sheet 2: High Risk Users (if RiskScore column exists)
        if 'RiskScore' in df.columns:
            high_risk_df = df[df['RiskScore'] > 60].copy()
            if not high_risk_df.empty:
                high_risk_df.to_excel(writer, sheet_name='High Risk Users', index=False)
        
        # Sheet 3: Summary Statistics
        if include_summary:
            summary_data = create_summary_data(df)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    output.seek(0)
    return output


def create_summary_data(df: pd.DataFrame) -> dict:
    """Create summary statistics dictionary."""
    summary = {
        'Metric': [],
        'Value': []
    }
    
    # Basic counts
    summary['Metric'].append('Total Users')
    summary['Value'].append(len(df))
    
    # Risk score stats
    if 'RiskScore' in df.columns:
        summary['Metric'].append('Average Risk Score')
        summary['Value'].append(round(df['RiskScore'].mean(), 1))
        
        summary['Metric'].append('Max Risk Score')
        summary['Value'].append(df['RiskScore'].max())
        
        summary['Metric'].append('Low Risk Users (0-30)')
        summary['Value'].append(len(df[df['RiskScore'] <= 30]))
        
        summary['Metric'].append('Medium Risk Users (31-60)')
        summary['Value'].append(len(df[(df['RiskScore'] > 30) & (df['RiskScore'] <= 60)]))
        
        summary['Metric'].append('High Risk Users (61-80)')
        summary['Value'].append(len(df[(df['RiskScore'] > 60) & (df['RiskScore'] <= 80)]))
        
        summary['Metric'].append('Critical Risk Users (81+)')
        summary['Value'].append(len(df[df['RiskScore'] > 80]))
    
    # Login stats
    if 'LastLoginDays' in df.columns:
        summary['Metric'].append('Average Last Login (days)')
        summary['Value'].append(round(df['LastLoginDays'].mean(), 1))
        
        summary['Metric'].append('Users Inactive 90+ Days')
        summary['Value'].append(len(df[df['LastLoginDays'] > 90]))
    
    # Access level distribution
    if 'AccessLevel' in df.columns:
        for level in df['AccessLevel'].unique():
            summary['Metric'].append(f'Users with {level} Access')
            summary['Value'].append(len(df[df['AccessLevel'] == level]))
    
    # Report metadata
    summary['Metric'].append('Report Generated')
    summary['Value'].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return summary


def export_to_pdf(df: pd.DataFrame, title: str = "Workspace Cleanup Report") -> BytesIO:
    """
    Export dataframe to PDF report.
    
    Includes:
    - Report header with title and date
    - Summary statistics
    - User data table (limited to first 50 rows for readability)
    - Recommendations section
    """
    from fpdf import FPDF
    
    output = BytesIO()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 15, title, ln=True, align='C')
    
    # Date
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    
    # Summary Section
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Executive Summary', ln=True)
    pdf.set_font('Helvetica', '', 11)
    
    total_users = len(df)
    pdf.cell(0, 8, f"Total Users Analyzed: {total_users}", ln=True)
    
    if 'RiskScore' in df.columns:
        high_risk = len(df[df['RiskScore'] > 60])
        critical = len(df[df['RiskScore'] > 80])
        avg_score = round(df['RiskScore'].mean(), 1)
        
        pdf.cell(0, 8, f"Average Risk Score: {avg_score}", ln=True)
        pdf.cell(0, 8, f"High Risk Users: {high_risk}", ln=True)
        pdf.cell(0, 8, f"Critical Risk Users: {critical}", ln=True)
    
    if 'LastLoginDays' in df.columns:
        inactive_90 = len(df[df['LastLoginDays'] > 90])
        pdf.cell(0, 8, f"Users Inactive 90+ Days: {inactive_90}", ln=True)
    
    pdf.ln(10)
    
    # Risk Distribution Section
    if 'RiskScore' in df.columns:
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Risk Distribution', ln=True)
        pdf.set_font('Helvetica', '', 11)
        
        low = len(df[df['RiskScore'] <= 30])
        medium = len(df[(df['RiskScore'] > 30) & (df['RiskScore'] <= 60)])
        high = len(df[(df['RiskScore'] > 60) & (df['RiskScore'] <= 80)])
        critical = len(df[df['RiskScore'] > 80])
        
        pdf.cell(0, 8, f"  Low Risk (0-30): {low} users ({round(low/total_users*100, 1)}%)", ln=True)
        pdf.cell(0, 8, f"  Medium Risk (31-60): {medium} users ({round(medium/total_users*100, 1)}%)", ln=True)
        pdf.cell(0, 8, f"  High Risk (61-80): {high} users ({round(high/total_users*100, 1)}%)", ln=True)
        pdf.cell(0, 8, f"  Critical Risk (81+): {critical} users ({round(critical/total_users*100, 1)}%)", ln=True)
        pdf.ln(10)
    
    # High Risk Users Table
    if 'RiskScore' in df.columns:
        high_risk_df = df[df['RiskScore'] > 60].head(20)
        if not high_risk_df.empty:
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'High Risk Users (Top 20)', ln=True)
            pdf.set_font('Helvetica', '', 9)
            
            # Table header
            pdf.set_fill_color(66, 66, 66)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(50, 8, 'Name', border=1, fill=True)
            pdf.cell(60, 8, 'Email', border=1, fill=True)
            pdf.cell(30, 8, 'Risk Score', border=1, fill=True)
            pdf.cell(40, 8, 'Last Login (days)', border=1, ln=True, fill=True)
            
            # Table rows
            pdf.set_text_color(0, 0, 0)
            for _, row in high_risk_df.iterrows():
                name = str(row.get('Name', 'N/A'))[:20]
                email = str(row.get('Email', 'N/A'))[:25]
                score = str(row.get('RiskScore', 'N/A'))
                days = str(row.get('LastLoginDays', 'N/A'))
                
                pdf.cell(50, 7, name, border=1)
                pdf.cell(60, 7, email, border=1)
                pdf.cell(30, 7, score, border=1)
                pdf.cell(40, 7, days, border=1, ln=True)
            
            pdf.ln(10)
    
    # Recommendations
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Recommendations', ln=True)
    pdf.set_font('Helvetica', '', 11)
    
    recommendations = [
        "1. Review all Critical and High risk users immediately",
        "2. Contact managers for confirmation on flagged users",
        "3. Consider reducing access for users inactive 90+ days",
        "4. Schedule regular quarterly access reviews",
        "5. Document all access changes for compliance"
    ]
    
    for rec in recommendations:
        pdf.cell(0, 8, rec, ln=True)
    
    pdf.ln(10)
    
    # Footer
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 10, "This report was generated by Gemini Workspace Cleanup Planner.", ln=True)
    pdf.cell(0, 8, "All recommendations should be reviewed by IT administrators before implementation.", ln=True)
    
    # Write to BytesIO
    pdf_bytes = pdf.output()
    output.write(pdf_bytes)
    output.seek(0)
    
    return output
