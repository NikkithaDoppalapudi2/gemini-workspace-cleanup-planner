import streamlit as st
import pandas as pd
from src.load_data import load_users
from src.cleanup_planner import build_prompt
from src.gemini_client import call_gemini

st.set_page_config(
    page_title="Gemini Workspace Cleanup Planner",
    page_icon="🧹",
    layout="wide"
)

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
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.title("🧹 Gemini-Assisted Google Workspace Cleanup Planner")
st.caption("Human-reviewed • AI-assisted • Safe by design")

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["📂 Upload Data", "🤖 AI Cleanup Plan", "🛡️ SOP & Risk Review"])

# ---------- TAB 1: Upload ----------
with tab1:
    st.subheader("Upload Google Workspace User Data")
    st.write("Upload a CSV export of users (Admin console / reports).")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully")
        st.dataframe(df, use_container_width=True)

# ---------- TAB 2: AI Cleanup ----------
with tab2:
    st.subheader("Generate AI-Assisted Cleanup Plan")

    if uploaded_file:
        with open("prompts/cleanup_prompt.txt") as f:
            base_prompt = f.read()

        final_prompt = build_prompt(df, base_prompt)

        if st.button("🚀 Generate Cleanup Plan with Gemini"):
            with st.spinner("Gemini is organizing the data safely..."):
                try:
                    output = call_gemini(final_prompt)
                    
                    # Clean the output
                    output = output.strip().lstrip('```csv').rstrip('```').strip()

                    # Parse CSV output and display as table
                    from io import StringIO
                    df_output = pd.read_csv(StringIO(output))
                    st.subheader("Cleanup Plan Results")
                    
                    # Convert to markdown table with bold headers
                    table_md = df_output.to_markdown(index=False)
                    # Make headers bold
                    lines = table_md.split('\n')
                    if len(lines) > 1:
                        lines[0] = '| ' + ' | '.join(['**' + col.strip() + '**' for col in lines[0].split('|')[1:-1]]) + ' |'
                    table_md = '\n'.join(lines)
                    st.markdown(table_md)

                    st.dataframe(df_output, use_container_width=True)  # Keep dataframe for reference

                    st.download_button(
                        label="⬇️ Download Cleanup Report",
                        data=output,
                        file_name="cleanup_report.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Failed to generate cleanup plan: {str(e)}")
                    st.info("Please check your API key and try again.")
    else:
        st.info("Please upload a CSV file first.")

# ---------- TAB 3: SOP & Risk ----------
with tab3:
    st.subheader("SOP & Risk Awareness")

    st.markdown("""
### ✅ What this tool does
- Organizes Workspace users for review
- Flags inactive or risky access
- Keeps **all decisions human-reviewed**

### ⚠️ What this tool does NOT do
- No automatic deletions
- No permission changes
- No admin actions

### 🛡️ Security Principles
- Least privilege
- Manual verification
- Documented changes
- Easy rollback
""")