import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
from datetime import datetime
import time

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
    page_title="Workspace Insights Pro",
    page_icon="🛡️",
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

# ---------- Custom Styling (Professional UI) ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 50% 50%, #1e293b 0%, #0f172a 100%);
    color: #f8fafc;
}

/* Header Styling */
.main-header {
    display: flex;
    align-items: center;
    padding: 1.5rem 0;
    margin-bottom: 2rem;
    border-bottom: 1px solid #334155;
}

.header-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin-left: 1rem;
    background: linear-gradient(90deg, #f8fafc, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    background-color: transparent;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #94a3b8;
    font-weight: 500;
    padding: 10px 20px;
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    border-color: #6366f1;
    color: #f8fafc;
}

.stTabs [aria-selected="true"] {
    background-color: #6366f1 !important;
    border-color: #6366f1 !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Card Styling */
.metric-container {
    background: rgba(30, 41, 59, 0.5);
    backdrop-filter: blur(10px);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.5rem;
    transition: transform 0.2s ease;
}

.metric-container:hover {
    transform: translateY(-5px);
    border-color: #475569;
}

/* Dataframe styling */
div[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 8px;
    overflow: hidden;
}

/* Custom button styling */
.stButton>button {
    background-color: #6366f1;
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    transition: all 0.2s ease;
}

.stButton>button:hover {
    background-color: #4f46e5;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    transform: scale(1.02);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #0f172a;
    border-right: 1px solid #334155;
}

/* Risk indicators */
.risk-dot {
    height: 10px;
    width: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
}
.dot-low { background-color: #22c55e; }
.dot-medium { background-color: #eab308; }
.dot-high { background-color: #f97316; }
.dot-critical { background-color: #ef4444; }

</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
col1, col2 = st.columns([0.1, 0.9])
with col1:
    try:
        st.image("assets/logo.png", width=80)
    except:
        st.write("🛡️") # Fallback icon

with col2:
    st.markdown('<div class="header-title">Workspace Insights Pro</div>', unsafe_allow_html=True)
    st.caption("Enterprise-grade Google Workspace Audit & Intelligence Platform")

st.divider()

# ---------- Sidebar: History & Branding ----------
with st.sidebar:
    st.markdown("### Workspace Insights")
    st.caption("v2.0.0 Enterprise Edition")
    st.divider()
    
    st.header("Analysis History")
    
    if st.session_state.analysis_history:
        for i, analysis in enumerate(reversed(st.session_state.analysis_history[-5:])):
            with st.expander(f"Report {len(st.session_state.analysis_history) - i}"):
                st.write(f"Users: {analysis['user_count']}")
                st.write(f"Date: {analysis['timestamp'][:16]}")
                if st.button(f"Restore Analysis #{len(st.session_state.analysis_history) - i}", key=f"load_{i}"):
                    st.session_state.current_analysis = analysis['result']
                    st.rerun()
        
        if st.button("Clear History", use_container_width=True):
            st.session_state.analysis_history = []
            st.rerun()
    else:
        st.info("No reports generated yet.")
    
    st.divider()
    st.markdown("---")
    st.caption("© 2026 Workspace Insights Inc.")

# ---------- Tabs ----------
tab_upload, tab_analytics, tab_ai, tab_email, tab_export, tab_compliance = st.tabs([
    "Data Source", 
    "Analytics", 
    "Intelligence", 
    "Communication",
    "Export",
    "Compliance & Risk"
])

# ---------- TAB 1: Data Source ----------
with tab_upload:
    st.subheader("Data Source Integration")
    st.write("Import user data from Google Workspace Admin Console for classification.")

    uploaded_file = st.file_uploader("Select Workspace Export (CSV)", type=["csv"])

    if uploaded_file:
        # Read and process data
        df = pd.read_csv(uploaded_file)
        
        # Add risk scores
        df = add_risk_scores(df)
        st.session_state.uploaded_data = df
        
        st.success(f"System verified: {len(df)} user records loaded.")
        
        # ---------- Filter & Search Section ----------
        st.divider()
        st.subheader("Search & Filter Intelligence")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("Search Name or Email", placeholder="e.g. John Doe")
        
        with col2:
            roles = ['All Roles'] + list(df['Role'].unique()) if 'Role' in df.columns else ['All Roles']
            selected_role = st.selectbox("Role Classification", roles)
        
        with col3:
            access_levels = ['All Levels'] + list(df['AccessLevel'].unique()) if 'AccessLevel' in df.columns else ['All Levels']
            selected_access = st.selectbox("Access Privilege", access_levels)
        
        # Risk score slider
        if 'RiskScore' in df.columns:
            min_risk, max_risk = int(df['RiskScore'].min()), int(df['RiskScore'].max())
            risk_range = st.slider(
                "Risk Score Threshold",
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
        
        if selected_role != 'All Roles' and 'Role' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Role'] == selected_role]
        
        if selected_access != 'All Levels' and 'AccessLevel' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['AccessLevel'] == selected_access]
        
        if 'RiskScore' in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df['RiskScore'] >= risk_range[0]) & 
                (filtered_df['RiskScore'] <= risk_range[1])
            ]
        
        st.session_state.filtered_data = filtered_df
        
        # Display data
        st.divider()
        st.subheader(f"Data Grid ({len(filtered_df)} users)")
        
        # Column reorder
        cols = list(filtered_df.columns)
        if 'RiskScore' in cols and 'RiskCategory' in cols:
            cols.remove('RiskScore')
            cols.remove('RiskCategory')
            cols = ['RiskCategory', 'RiskScore'] + cols
            filtered_df = filtered_df[cols]
        
        st.dataframe(filtered_df, use_container_width=True, height=400)

# ---------- TAB 2: Analytics Dashboard ----------
with tab_analytics:
    st.subheader("Intelligence Dashboard")
    
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        summary = get_risk_summary(df)
        
        # Metric Cards Row
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        with m_col1:
            st.metric("Total User Accounts", summary['total_users'])
        
        with m_col2:
            st.metric("High Risk Identified", summary['high_risk_total'],
                      delta=f"{round(summary['high_risk_total']/summary['total_users']*100, 1)}%",
                      delta_color="inverse")
        
        with m_col3:
            st.metric("Avg Security Score", summary['avg_score'])
        
        with m_col4:
            if 'LastLoginDays' in df.columns:
                avg_login = round(df['LastLoginDays'].mean(), 1)
                st.metric("Avg Activity Gap", f"{avg_login} days")
            else:
                st.metric("Avg Activity Gap", "N/A")
        
        st.divider()
        
        # Charts Row 1
        c_col1, c_col2 = st.columns(2)
        
        with c_col1:
            st.markdown("#### Security Risk Distribution")
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
                hole=0.5
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#f8fafc',
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with c_col2:
            st.markdown("#### Privilege Distribution")
            if 'AccessLevel' in df.columns:
                access_counts = df['AccessLevel'].value_counts().reset_index()
                access_counts.columns = ['AccessLevel', 'Count']
                
                fig_bar = px.bar(
                    access_counts,
                    x='AccessLevel',
                    y='Count',
                    color='AccessLevel',
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f8fafc',
                    showlegend=False,
                    xaxis_title=None,
                    yaxis_title=None
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Charts Row 2
        c_col1, c_col2 = st.columns(2)
        
        with c_col1:
            st.markdown("#### Organizational Roles")
            if 'Role' in df.columns:
                role_counts = df['Role'].value_counts().reset_index()
                role_counts.columns = ['Role', 'Count']
                
                fig_role = px.bar(
                    role_counts,
                    x='Count',
                    y='Role',
                    orientation='h',
                    color='Count',
                    color_continuous_scale='Blues'
                )
                fig_role.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f8fafc',
                    showlegend=False,
                    xaxis_title=None,
                    yaxis_title=None
                )
                st.plotly_chart(fig_role, use_container_width=True)
        
        with c_col2:
            st.markdown("#### Security Score Variance")
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
                    font_color='#f8fafc',
                    xaxis_title="Score Range",
                    yaxis_title="Count"
                )
                st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("System Ready: Please integrate a data source to generate dashboard.")

# ---------- TAB 3: AI Intelligence ----------
with tab_ai:
    st.subheader("AI-Driven Classification Intelligence")

    if st.session_state.filtered_data is not None:
        df = st.session_state.filtered_data
        
        st.info(f"Targeting {len(df)} user records for intelligence analysis.")
        
        with open("prompts/cleanup_prompt.txt") as f:
            base_prompt = f.read()

        final_prompt = build_prompt(df, base_prompt)
        
        if st.button("Generate Classification Plan", use_container_width=True):
            with st.spinner("Executing proprietary classification algorithms..."):
                try:
                    # Batch processing logic
                    if len(df) > 50:
                        results = []
                        chunk_size = 50
                        total_chunks = (len(df) + chunk_size - 1) // chunk_size
                        
                        p_bar = st.progress(0)
                        s_text = st.empty()
                        
                        for i in range(0, len(df), chunk_size):
                            chunk = df.iloc[i:i+chunk_size]
                            chunk_prompt = build_prompt(chunk, base_prompt)
                            s_text.text(f"Processing vector batch {i//chunk_size + 1} of {total_chunks}...")
                            
                            chunk_result = call_gemini(chunk_prompt)
                            
                            if chunk_result.startswith("Error:"):
                                st.error(f"Vector batch {i//chunk_size + 1} failed.")
                                fallback = [f"Needs Manager Confirmation,{r['Email']},Automated Review Failure" for _, r in chunk.iterrows()]
                                chunk_result = "Category,User,Notes\n" + "\n".join(fallback)
                            
                            cleaned = chunk_result.strip().lstrip('```csv').rstrip('```').strip()
                            if i > 0:
                                lines = cleaned.split('\n')
                                if len(lines) > 1: cleaned = '\n'.join(lines[1:])
                            
                            results.append(cleaned)
                            if i + chunk_size < len(df): time.sleep(2)
                            p_bar.progress(min((i + chunk_size) / len(df), 1.0))
                        
                        output = '\n'.join(results)
                        p_bar.empty()
                        s_text.empty()
                    else:
                        output = call_gemini(final_prompt).strip().lstrip('```csv').rstrip('```').strip()
                    
                    # Parse results
                    df_output = pd.read_csv(StringIO(output))
                    st.session_state.current_analysis = df_output
                    
                    # History
                    st.session_state.analysis_history.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'user_count': len(df),
                        'result': df_output
                    })
                    
                    st.success("Plan Generated Successfully.")
                    
                    # Metrics
                    if 'Category' in df_output.columns:
                        col1, col2, col3 = st.columns(3)
                        counts = df_output['Category'].value_counts()
                        col1.metric("Confirmed Active", counts.get('Safe to Keep', 0))
                        col2.metric("Pending Verification", counts.get('Needs Manager Confirmation', 0))
                        col3.metric("Decommissioning Target", counts.get('Likely Inactive - Review Required', 0))
                    
                    st.divider()
                    st.dataframe(df_output, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Intelligence execution failure: {str(e)}")
        
        # Restore previous
        if st.session_state.current_analysis is not None:
            st.divider()
            st.markdown("#### Active Report")
            st.dataframe(st.session_state.current_analysis, use_container_width=True)
    else:
        st.info("System Ready: Please integrate a data source first.")

# ---------- TAB 4: Communication ----------
with tab_email:
    st.subheader("Communication Strategy & Notifications")
    
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        
        template_type = st.selectbox(
            "Communication Template",
            get_template_options()
        )
        
        st.divider()
        
        if template_type == "Individual Manager Notification":
            col1, col2 = st.columns(2)
            with col1:
                selected_user = st.selectbox("Assignee Target", df['Name'].tolist())
                manager_name = st.text_input("Approver Name", "Manager")
            
            with col2:
                u_row = df[df['Name'] == selected_user].iloc[0]
                st.write("**Account Profile:**")
                st.write(f"Email: {u_row['Email']}")
                st.write(f"Security Category: {u_row.get('RiskCategory', 'N/A')}")
            
            if st.button("Generate Strategy"):
                email = generate_manager_notification(selected_user, u_row['Email'], u_row.get('RiskCategory', 'N/A'), u_row.get('LastLoginDays', 0), u_row.get('AccessLevel', 'N/A'), manager_name)
                st.text_area("Final Output", email, height=400)
        
        elif template_type == "Bulk Manager Notification":
            risk_filter = st.multiselect("Risk Thresholds", ['🟢 Low', '🟡 Medium', '🟠 High', '🔴 Critical'], default=['🟠 High', '🔴 Critical'])
            manager_name = st.text_input("Approver Name", "Manager")
            
            f_df = df[df['RiskCategory'].isin(risk_filter)] if 'RiskCategory' in df.columns else df
            st.write(f"Targeting {len(f_df)} account(s).")
            
            if st.button("Generate Bulk Strategy") and len(f_df) > 0:
                email = generate_bulk_notification(f_df, manager_name)
                st.text_area("Final Output", email, height=400)
        
        elif template_type == "Review Reminder":
            p_count = st.number_input("Pending Item Count", min_value=1, value=5)
            deadline = st.text_input("Compliance Deadline", "end of current business week")
            
            if st.button("Generate Reminder"):
                email = generate_review_reminder(p_count, deadline)
                st.text_area("Final Output", email, height=300)
    else:
        st.info("System Ready: Please integrate a data source first.")

# ---------- TAB 5: Export ----------
with tab_export:
    st.subheader("Reporting & Data Export")
    
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        st.write("Generate professional reports for stakeholders.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### Enterprise CSV")
            st.download_button("Download CSV", export_to_csv(df), file_name=f"audit_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
        
        with col2:
            st.markdown("##### Executive Excel")
            st.download_button("Download Excel", export_to_excel(df), file_name=f"audit_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        
        with col3:
            st.markdown("##### Compliance PDF")
            st.download_button("Download PDF", export_to_pdf(df, title="Workspace Security Audit"), file_name=f"report_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.info("System Ready: Output generation requires data source integration.")

# ---------- TAB 6: Compliance & Risk ----------
with tab_compliance:
    st.subheader("Compliance Framework & Risk Methodology")

    st.markdown("""
### 📋 System Operations
The **Workspace Insights Pro** platform provides architectural visibility into Google Workspace governance. 
- **Automated Auditing**: Continuous identification of inactive/high-privilege nodes.
- **Risk Attribution**: algorithmic scoring of security exposure.
- **Human-in-the-Loop**: All administrative actions require executive oversight.

### 🛡️ Core Security Principles
- **Least Privilege Implementation**: Validating that access is restricted to operational necessity.
- **Zero Trust Governance**: Continuous verification of account activity gaps.
- **Audit Traceability**: Documenting all review cycles for compliance requirements (SOC2, ISO 27001).

### 🏷️ Risk Attribution Methodology
| Variable | Attribution | Range |
|----------|-------------|-------|
| **Activity Gap** | Days since last authentication | 0 - 100 pts |
| **Access Scalar** | Privilege tier (Owner vs Viewer) | 10 - 60 pts |
| **Persona Scalar** | Account type risk premium | 0 - 20 pts |

### 🎯 Strategic Response Tiers
| Score | Classification | Operational Response |
|-------|----------------|----------------------|
| 0-30 | 🟢 Standard | Baseline monitoring |
| 31-60 | 🟡 Advisory | Quarterly validation |
| 61-80 | 🟠 Elevated | Immediate verification |
| 81+ | 🔴 Critical | Priority administrative review |
""")

st.divider()
st.caption("Powered by Workspace Insights Intelligent Analysis Engine.")