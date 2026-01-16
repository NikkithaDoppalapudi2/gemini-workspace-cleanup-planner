import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
from datetime import datetime

from src.load_data import load_users
from src.cleanup_planner import build_prompt
from src.gemini_client import call_gemini
from src.risk_calculator import add_risk_scores, get_risk_summary
from src.email_templates import (
    generate_manager_notification,
    generate_bulk_notification,
    generate_review_reminder,
    get_template_options
)
from src.export_utils import export_to_csv, export_to_excel, export_to_pdf

# ---------- Page Config ----------
st.set_page_config(
    page_title="Gemini Workspace Cleanup Planner",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Initialize Session State ----------
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

# ---------- Custom Styling ----------
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
}
h1, h2, h3 {
    color: #e5e7eb;
}
.stTabs [data-baseweb="tab"] {
    background-color: #1e293b;
    color: #e5e7eb;
    border-radius: 10px;
    padding: 10px;
}
.stTabs [aria-selected="true"] {
    background-color: #6366f1;
}
.stDataFrame {
    background-color: #020617;
}
.metric-card {
    background: linear-gradient(135deg, #1e293b, #334155);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    border: 1px solid #475569;
}
.metric-value {
    font-size: 2.5rem;
    font-weight: bold;
    color: #6366f1;
}
.metric-label {
    font-size: 0.9rem;
    color: #94a3b8;
    margin-top: 5px;
}
.risk-low { color: #22c55e; }
.risk-medium { color: #eab308; }
.risk-high { color: #f97316; }
.risk-critical { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.title("🧹 Gemini-Assisted Google Workspace Cleanup Planner")
st.caption("Human-reviewed • AI-assisted • Safe by design")

# ---------- Sidebar: History ----------
with st.sidebar:
    st.header("📜 Analysis History")
    
    if st.session_state.analysis_history:
        for i, analysis in enumerate(reversed(st.session_state.analysis_history[-5:])):
            with st.expander(f"Analysis {len(st.session_state.analysis_history) - i}: {analysis['timestamp'][:10]}"):
                st.write(f"**Users analyzed:** {analysis['user_count']}")
                st.write(f"**Time:** {analysis['timestamp']}")
                if st.button(f"Load Analysis #{len(st.session_state.analysis_history) - i}", key=f"load_{i}"):
                    st.session_state.current_analysis = analysis['result']
                    st.rerun()
        
        if st.button("🗑️ Clear History"):
            st.session_state.analysis_history = []
            st.rerun()
    else:
        st.info("No analysis history yet. Generate a cleanup plan to start.")
    
    st.divider()
    st.caption("💡 Tip: Your last 5 analyses are saved during this session.")

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📂 Upload Data", 
    "📊 Analytics", 
    "🤖 AI Cleanup Plan", 
    "📧 Email Templates",
    "📥 Export",
    "🛡️ SOP & Risk"
])

# ---------- TAB 1: Upload & Filter ----------
with tab1:
    st.subheader("Upload Google Workspace User Data")
    st.write("Upload a CSV export of users (Admin console / reports).")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        # Read and process data
        df = pd.read_csv(uploaded_file)
        
        # Add risk scores
        df = add_risk_scores(df)
        st.session_state.uploaded_data = df
        
        st.success(f"✅ File uploaded successfully! {len(df)} users loaded.")
        
        # ---------- Filter & Search Section ----------
        st.divider()
        st.subheader("🔍 Filter & Search")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Search by name/email
            search_term = st.text_input("🔎 Search by Name or Email", "")
        
        with col2:
            # Filter by role
            roles = ['All'] + list(df['Role'].unique()) if 'Role' in df.columns else ['All']
            selected_role = st.selectbox("👤 Filter by Role", roles)
        
        with col3:
            # Filter by access level
            access_levels = ['All'] + list(df['AccessLevel'].unique()) if 'AccessLevel' in df.columns else ['All']
            selected_access = st.selectbox("🔐 Filter by Access Level", access_levels)
        
        # Risk score slider
        if 'RiskScore' in df.columns:
            min_risk, max_risk = int(df['RiskScore'].min()), int(df['RiskScore'].max())
            risk_range = st.slider(
                "⚠️ Risk Score Range",
                min_value=min_risk,
                max_value=max_risk,
                value=(min_risk, max_risk)
            )
        else:
            risk_range = (0, 200)
        
        # Apply filters
        filtered_df = df.copy()
        
        if search_term:
            mask = (
                filtered_df['Name'].str.contains(search_term, case=False, na=False) |
                filtered_df['Email'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        if selected_role != 'All' and 'Role' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Role'] == selected_role]
        
        if selected_access != 'All' and 'AccessLevel' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['AccessLevel'] == selected_access]
        
        if 'RiskScore' in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df['RiskScore'] >= risk_range[0]) & 
                (filtered_df['RiskScore'] <= risk_range[1])
            ]
        
        st.session_state.filtered_data = filtered_df
        
        # Display filtered data
        st.divider()
        st.subheader(f"📋 User Data ({len(filtered_df)} users)")
        
        # Column reorder to show risk first
        cols = list(filtered_df.columns)
        if 'RiskScore' in cols and 'RiskCategory' in cols:
            cols.remove('RiskScore')
            cols.remove('RiskCategory')
            cols = ['RiskCategory', 'RiskScore'] + cols
            filtered_df = filtered_df[cols]
        
        st.dataframe(filtered_df, use_container_width=True, height=400)

# ---------- TAB 2: Analytics Dashboard ----------
with tab2:
    st.subheader("📊 Analytics Dashboard")
    
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        summary = get_risk_summary(df)
        
        # Metric Cards Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👥 Total Users",
                value=summary['total_users']
            )
        
        with col2:
            st.metric(
                label="⚠️ High Risk Users",
                value=summary['high_risk_total'],
                delta=f"{round(summary['high_risk_total']/summary['total_users']*100, 1)}% of total" if summary['total_users'] > 0 else "0%",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                label="📊 Avg Risk Score",
                value=summary['avg_score']
            )
        
        with col4:
            if 'LastLoginDays' in df.columns:
                avg_login = round(df['LastLoginDays'].mean(), 1)
                st.metric(
                    label="📅 Avg Last Login",
                    value=f"{avg_login} days"
                )
            else:
                st.metric(label="📅 Avg Last Login", value="N/A")
        
        st.divider()
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk Category Pie Chart
            st.subheader("🥧 Risk Distribution")
            risk_data = pd.DataFrame({
                'Category': ['Low', 'Medium', 'High', 'Critical'],
                'Count': [summary['low_count'], summary['medium_count'], 
                         summary['high_count'], summary['critical_count']]
            })
            risk_data = risk_data[risk_data['Count'] > 0]
            
            fig_pie = px.pie(
                risk_data, 
                values='Count', 
                names='Category',
                color='Category',
                color_discrete_map={
                    'Low': '#22c55e',
                    'Medium': '#eab308',
                    'High': '#f97316',
                    'Critical': '#ef4444'
                },
                hole=0.4
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e5e7eb'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Access Level Bar Chart
            st.subheader("🔐 Access Level Distribution")
            if 'AccessLevel' in df.columns:
                access_counts = df['AccessLevel'].value_counts().reset_index()
                access_counts.columns = ['AccessLevel', 'Count']
                
                fig_bar = px.bar(
                    access_counts,
                    x='AccessLevel',
                    y='Count',
                    color='AccessLevel',
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#e5e7eb',
                    showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No AccessLevel column found in data.")
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            # Role Distribution
            st.subheader("👥 Role Distribution")
            if 'Role' in df.columns:
                role_counts = df['Role'].value_counts().reset_index()
                role_counts.columns = ['Role', 'Count']
                
                fig_role = px.bar(
                    role_counts,
                    x='Count',
                    y='Role',
                    orientation='h',
                    color='Count',
                    color_continuous_scale='Viridis'
                )
                fig_role.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#e5e7eb',
                    showlegend=False
                )
                st.plotly_chart(fig_role, use_container_width=True)
            else:
                st.info("No Role column found in data.")
        
        with col2:
            # Risk Score Histogram
            st.subheader("📈 Risk Score Histogram")
            if 'RiskScore' in df.columns:
                fig_hist = px.histogram(
                    df,
                    x='RiskScore',
                    nbins=20,
                    color_discrete_sequence=['#6366f1']
                )
                fig_hist.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#e5e7eb',
                    xaxis_title='Risk Score',
                    yaxis_title='Number of Users'
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("No RiskScore data available.")
        
        # Last Login Analysis
        st.divider()
        st.subheader("📅 Login Activity Analysis")
        
        if 'LastLoginDays' in df.columns:
            col1, col2, col3, col4 = st.columns(4)
            
            active_30 = len(df[df['LastLoginDays'] <= 30])
            active_90 = len(df[(df['LastLoginDays'] > 30) & (df['LastLoginDays'] <= 90)])
            inactive_90 = len(df[(df['LastLoginDays'] > 90) & (df['LastLoginDays'] <= 180)])
            inactive_180 = len(df[df['LastLoginDays'] > 180])
            
            col1.metric("🟢 Active (0-30 days)", active_30)
            col2.metric("🟡 Recent (31-90 days)", active_90)
            col3.metric("🟠 Inactive (91-180 days)", inactive_90)
            col4.metric("🔴 Long Inactive (180+ days)", inactive_180)
    else:
        st.info("📂 Please upload a CSV file in the 'Upload Data' tab to view analytics.")

# ---------- TAB 3: AI Cleanup Plan ----------
with tab3:
    st.subheader("Generate AI-Assisted Cleanup Plan")

    if st.session_state.filtered_data is not None:
        df = st.session_state.filtered_data
        
        # Show current filter status
        total_uploaded = len(st.session_state.uploaded_data) if st.session_state.uploaded_data is not None else 0
        st.info(f"📊 Analyzing {len(df)} users (filtered from {total_uploaded} total)")
        
        with open("prompts/cleanup_prompt.txt") as f:
            base_prompt = f.read()

        final_prompt = build_prompt(df, base_prompt)
        
        # Batch processing info
        if len(df) > 50:
            st.warning(f"⚡ Large dataset detected ({len(df)} users). Processing will be done in batches.")
        
        if st.button("🚀 Generate Cleanup Plan with Gemini"):
            with st.spinner("Gemini is organizing the data safely..."):
                try:
                    # Batch processing for large files
                    if len(df) > 50:
                        results = []
                        chunk_size = 50
                        total_chunks = (len(df) + chunk_size - 1) // chunk_size
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i in range(0, len(df), chunk_size):
                            chunk = df.iloc[i:i+chunk_size]
                            chunk_prompt = build_prompt(chunk, base_prompt)
                            chunk_result = call_gemini(chunk_prompt)
                            
                            # Clean the chunk result
                            chunk_result = chunk_result.strip().lstrip('```csv').rstrip('```').strip()
                            
                            # Skip header for subsequent chunks
                            if i > 0:
                                lines = chunk_result.split('\n')
                                if len(lines) > 1:
                                    chunk_result = '\n'.join(lines[1:])
                            
                            results.append(chunk_result)
                            
                            # Update progress
                            progress = min((i + chunk_size) / len(df), 1.0)
                            progress_bar.progress(progress)
                            status_text.text(f"Processing batch {i//chunk_size + 1} of {total_chunks}...")
                        
                        output = '\n'.join(results)
                        progress_bar.empty()
                        status_text.empty()
                    else:
                        output = call_gemini(final_prompt)
                        output = output.strip().lstrip('```csv').rstrip('```').strip()
                    
                    # Parse and display results
                    df_output = pd.read_csv(StringIO(output))
                    st.session_state.current_analysis = df_output
                    
                    # Save to history
                    st.session_state.analysis_history.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'user_count': len(df),
                        'result': df_output
                    })
                    
                    st.subheader("✅ Cleanup Plan Results")
                    
                    # Summary metrics
                    if 'Category' in df_output.columns:
                        col1, col2, col3 = st.columns(3)
                        categories = df_output['Category'].value_counts()
                        
                        safe = categories.get('Safe to Keep', 0)
                        review = categories.get('Needs Manager Confirmation', 0)
                        inactive = categories.get('Likely Inactive - Review Required', 0)
                        
                        col1.metric("✅ Safe to Keep", safe)
                        col2.metric("⚠️ Needs Confirmation", review)
                        col3.metric("🔴 Review Required", inactive)
                    
                    st.divider()
                    
                    # Display table
                    st.dataframe(df_output, use_container_width=True)

                    st.download_button(
                        label="⬇️ Download Cleanup Report (CSV)",
                        data=output,
                        file_name="cleanup_report.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"Failed to generate cleanup plan: {str(e)}")
                    st.info("Please check your API key and try again.")
        
        # Show previous analysis if available
        if st.session_state.current_analysis is not None and not st.button("🚀 Generate Cleanup Plan with Gemini", key="hidden"):
            st.divider()
            st.subheader("📋 Previous Analysis Results")
            st.dataframe(st.session_state.current_analysis, use_container_width=True)
    else:
        st.info("📂 Please upload a CSV file first in the 'Upload Data' tab.")

# ---------- TAB 4: Email Templates ----------
with tab4:
    st.subheader("📧 Email Template Generator")
    
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        
        template_type = st.selectbox(
            "Select Template Type",
            get_template_options()
        )
        
        st.divider()
        
        if template_type == "Individual Manager Notification":
            st.write("Generate an email for a specific user:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # User selection
                user_names = df['Name'].tolist()
                selected_user = st.selectbox("Select User", user_names)
                manager_name = st.text_input("Manager Name", "Manager")
            
            with col2:
                user_row = df[df['Name'] == selected_user].iloc[0]
                st.write("**User Details:**")
                st.write(f"- Email: {user_row['Email']}")
                st.write(f"- Risk: {user_row.get('RiskCategory', 'N/A')}")
                st.write(f"- Last Login: {user_row.get('LastLoginDays', 'N/A')} days")
            
            if st.button("Generate Email"):
                email = generate_manager_notification(
                    user_name=selected_user,
                    user_email=user_row['Email'],
                    risk_category=user_row.get('RiskCategory', 'Unknown'),
                    last_login_days=user_row.get('LastLoginDays', 0),
                    access_level=user_row.get('AccessLevel', 'Unknown'),
                    manager_name=manager_name
                )
                
                st.text_area("Generated Email", email, height=400)
                st.download_button(
                    "📋 Download Email Template",
                    email,
                    file_name=f"email_{selected_user.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
        
        elif template_type == "Bulk Manager Notification":
            st.write("Generate a bulk email for multiple flagged users:")
            
            # Filter options
            risk_filter = st.multiselect(
                "Include users with risk categories:",
                ['🟢 Low', '🟡 Medium', '🟠 High', '🔴 Critical'],
                default=['🟠 High', '🔴 Critical']
            )
            
            manager_name = st.text_input("Manager Name", "Manager", key="bulk_manager")
            
            # Filter dataframe
            if 'RiskCategory' in df.columns:
                filtered_for_email = df[df['RiskCategory'].isin(risk_filter)]
            else:
                filtered_for_email = df
            
            st.write(f"**{len(filtered_for_email)} users will be included**")
            
            if st.button("Generate Bulk Email") and len(filtered_for_email) > 0:
                email = generate_bulk_notification(filtered_for_email, manager_name)
                
                st.text_area("Generated Email", email, height=400)
                st.download_button(
                    "📋 Download Email Template",
                    email,
                    file_name="bulk_notification_email.txt",
                    mime="text/plain"
                )
        
        elif template_type == "Review Reminder":
            st.write("Generate a reminder email for pending reviews:")
            
            pending_count = st.number_input("Number of Pending Reviews", min_value=1, value=5)
            deadline = st.text_input("Deadline", "end of this week")
            
            if st.button("Generate Reminder"):
                email = generate_review_reminder(pending_count, deadline)
                
                st.text_area("Generated Email", email, height=300)
                st.download_button(
                    "📋 Download Email Template",
                    email,
                    file_name="review_reminder_email.txt",
                    mime="text/plain"
                )
    else:
        st.info("📂 Please upload a CSV file first to generate email templates.")

# ---------- TAB 5: Export ----------
with tab5:
    st.subheader("📥 Export Options")
    
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        
        st.write("Export your data in various formats:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📄 CSV Export")
            st.write("Simple comma-separated format")
            csv_data = export_to_csv(df)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"workspace_users_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.markdown("### 📊 Excel Export")
            st.write("Multi-sheet workbook with summary")
            excel_data = export_to_excel(df)
            st.download_button(
                label="⬇️ Download Excel",
                data=excel_data,
                file_name=f"workspace_users_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            st.markdown("### 📑 PDF Report")
            st.write("Formatted report with charts")
            pdf_data = export_to_pdf(df)
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_data,
                file_name=f"workspace_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
        
        st.divider()
        
        # Export AI Analysis Results
        if st.session_state.current_analysis is not None:
            st.subheader("📋 Export AI Analysis Results")
            
            analysis_df = st.session_state.current_analysis
            
            col1, col2 = st.columns(2)
            
            with col1:
                analysis_csv = export_to_csv(analysis_df)
                st.download_button(
                    label="⬇️ Download Analysis (CSV)",
                    data=analysis_csv,
                    file_name=f"cleanup_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                analysis_excel = export_to_excel(analysis_df, include_summary=False)
                st.download_button(
                    label="⬇️ Download Analysis (Excel)",
                    data=analysis_excel,
                    file_name=f"cleanup_analysis_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info("📂 Please upload a CSV file first to export data.")

# ---------- TAB 6: SOP & Risk ----------
with tab6:
    st.subheader("SOP & Risk Awareness")

    st.markdown("""
### ✅ What this tool does
- Organizes Workspace users for review
- Flags inactive or risky access
- Calculates risk scores automatically
- Generates analytics and reports
- Creates email templates for manager notifications
- Keeps **all decisions human-reviewed**

### ⚠️ What this tool does NOT do
- No automatic deletions
- No permission changes
- No admin actions
- No direct API modifications

### 🛡️ Security Principles
- Least privilege
- Manual verification
- Documented changes
- Easy rollback

### 📊 Risk Score Calculation
The risk score is calculated based on:
- **Last Login Days**: More days = higher risk
  - 0-30 days: 0 points
  - 31-90 days: 25 points
  - 91-180 days: 50 points
  - 181-365 days: 75 points
  - 365+ days: 100 points

- **Access Level**: Higher access = higher risk
  - Viewer: 10 points
  - Commenter: 20 points
  - Editor: 40 points
  - Owner: 60 points

- **Role Bonus**: Certain roles add 20 points
  - Former Employee
  - Contractor
  - Intern
  - Temporary

### 🎯 Risk Categories
| Score Range | Category | Action |
|-------------|----------|--------|
| 0-30 | 🟢 Low | Monitor normally |
| 31-60 | 🟡 Medium | Review quarterly |
| 61-80 | 🟠 High | Review immediately |
| 81+ | 🔴 Critical | Urgent action needed |
""")