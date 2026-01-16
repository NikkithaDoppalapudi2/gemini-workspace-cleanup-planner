# 🧹 Gemini Workspace Cleanup Planner

A safe, AI-assisted tool for organizing Google Workspace user data and planning cleanup actions. Built with Streamlit and Google's Gemini AI, this app helps administrators review inactive or risky user accounts without performing any automated deletions.

## ✨ Features

### Core Features
- **Upload CSV Data**: Import user data from Google Workspace admin exports
- **AI-Powered Analysis**: Uses Gemini 1.5 Flash to categorize users into:
  - Safe to Keep
  - Needs Manager Confirmation
  - Likely Inactive - Review Required
- **Human-Safe Design**: No automatic actions - all decisions remain human-reviewed
- **Beautiful UI**: Dark-themed Streamlit interface with 6 organized tabs

### 📊 Analytics Dashboard
- **Summary Statistics**: Total users, high-risk count, average risk score
- **Interactive Charts**: 
  - Risk distribution pie chart
  - Access level bar chart
  - Role distribution chart
  - Risk score histogram
- **Login Activity Analysis**: Categorized by activity level (active, recent, inactive)

### ⚠️ Risk Score Calculator
Automatic risk scoring based on:
- **Last Login Days**: 0-30 = 0pts, 31-90 = 25pts, 91-180 = 50pts, 181-365 = 75pts, 365+ = 100pts
- **Access Level**: Viewer = 10pts, Commenter = 20pts, Editor = 40pts, Owner = 60pts
- **Role Bonus**: Former Employee, Contractor, Intern, Temporary = +20pts

Risk Categories:
| Score | Category | Action |
|-------|----------|--------|
| 0-30 | 🟢 Low | Monitor normally |
| 31-60 | 🟡 Medium | Review quarterly |
| 61-80 | 🟠 High | Review immediately |
| 81+ | 🔴 Critical | Urgent action needed |

### 🔍 Filter & Search
- Search by name or email
- Filter by role
- Filter by access level
- Risk score range slider

### 📧 Email Template Generator
- **Individual Manager Notification**: Generate personalized emails for specific users
- **Bulk Manager Notification**: Send consolidated emails for multiple flagged users
- **Review Reminder**: Create deadline reminder emails

### ⚡ Batch Processing
- Handles large CSV files (50+ users) efficiently
- Progress bar during AI analysis
- Chunked processing to avoid API limits

### 📜 Session History
- Automatically saves last 5 analyses
- Sidebar history viewer
- Quick restore previous results

### 📥 Export Options
- **CSV**: Simple comma-separated format
- **Excel**: Multi-sheet workbook with summary statistics
- **PDF**: Formatted report with recommendations

## 🛡️ Safety & Compliance

This tool follows strict safety principles:
- ✅ Organizes data for review
- ✅ Flags inactive/risky access
- ✅ Keeps all decisions human-reviewed
- ❌ No automatic deletions
- ❌ No permission changes
- ❌ No admin API actions

## 🚀 Quick Start

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/NikkithaDoppalapudi2/gemini-workspace-cleanup-planner.git
   cd gemini-workspace-cleanup-planner
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key**:
   - Copy `.env.example` to `.env`
   - Add your Gemini API key: `GEMINI_API_KEY=your_key_here`
   - Get a free API key from [Google AI Studio](https://aistudio.google.com/)

5. **Run the app**:
   ```bash
   streamlit run app.py
   ```
   Access at `http://localhost:8501`

### Sample Data

Use `data/sample_users.csv` for testing. It contains 25 sample users with columns:
- Name
- Email
- Role
- LastLoginDays
- AccessLevel

## 🌐 Deployment

### Streamlit Community Cloud

1. **Push to GitHub** (already done if following this repo)

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select this repository
   - Set main file path: `app.py`
   - Deploy

3. **Add Secrets**:
   - In app settings, add: `GEMINI_API_KEY = "your_api_key"`

Your app will be live at a URL like `https://your-app-name.streamlit.app`

## 📋 Usage

1. **Upload Data**: Use the "📂 Upload Data" tab to import your CSV
2. **View Analytics**: Check the "📊 Analytics" tab for dashboard insights
3. **Generate Plan**: Click "🚀 Generate Cleanup Plan with Gemini" in the "🤖 AI Cleanup Plan" tab
4. **Create Emails**: Use "📧 Email Templates" to generate manager notifications
5. **Export Results**: Download your data in CSV, Excel, or PDF format
6. **SOP Review**: Check the "🛡️ SOP & Risk Review" tab for safety guidelines

## 🏗️ Project Structure

```
gemini-workspace-cleanup-planner/
├── app.py                     # Main Streamlit app (6 tabs)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── data/
│   └── sample_users.csv      # Sample user data (25 users)
├── prompts/
│   └── cleanup_prompt.txt    # AI prompt template
├── src/
│   ├── gemini_client.py      # Gemini AI integration
│   ├── load_data.py          # Data loading utilities
│   ├── cleanup_planner.py    # Prompt building
│   ├── risk_calculator.py    # Risk score calculation
│   ├── email_templates.py    # Email template generation
│   ├── export_utils.py       # CSV, Excel, PDF export
│   └── main.py               # CLI version
└── output/                   # Generated reports (ignored)
```

## 🔧 Dependencies

- `streamlit` - Web application framework
- `pandas` - Data manipulation
- `google-generativeai` - Gemini AI SDK
- `plotly` - Interactive charts
- `openpyxl` - Excel export
- `fpdf2` - PDF generation
- `python-dotenv` - Environment variable management
- `tabulate` - Table formatting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test locally
4. Commit: `git commit -m 'Add feature'`
5. Push: `git push origin feature-name`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for planning and analysis only. Always verify AI recommendations manually before taking any actions in your Google Workspace environment. The authors are not responsible for any unintended consequences of using this tool.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini AI](https://ai.google.dev/)
- Charts by [Plotly](https://plotly.com/)
- Inspired by safe IT administration practices