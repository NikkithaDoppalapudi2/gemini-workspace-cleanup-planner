# 🧹 Gemini Workspace Cleanup Planner

A safe, AI-assisted tool for organizing Google Workspace user data and planning cleanup actions. Built with Streamlit and Google's Gemini AI, this app helps administrators review inactive or risky user accounts without performing any automated deletions.

## ✨ Features

- **Upload CSV Data**: Import user data from Google Workspace admin exports
- **AI-Powered Analysis**: Uses Gemini 2.5 Flash to categorize users into:
  - Safe to Keep
  - Needs Manager Confirmation
  - Likely Inactive - Review Required
- **Human-Safe Design**: No automatic actions - all decisions remain human-reviewed
- **CSV Export**: Download categorized results for further processing
- **Beautiful UI**: Dark-themed Streamlit interface with tabbed navigation

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

Use `data/sample_users.csv` for testing. It contains sample user data with columns:
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
2. **Generate Plan**: Click "🚀 Generate Cleanup Plan with Gemini" in the "🤖 AI Cleanup Plan" tab
3. **Review Results**: View the categorized table and download CSV
4. **SOP Review**: Check the "🛡️ SOP & Risk Review" tab for safety guidelines

## 🏗️ Project Structure

```
gemini-workspace-cleanup-planner/
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── data/
│   └── sample_users.csv  # Sample user data
├── prompts/
│   └── cleanup_prompt.txt # AI prompt template
├── src/
│   ├── gemini_client.py   # Gemini AI integration
│   ├── load_data.py      # Data loading utilities
│   ├── cleanup_planner.py # Prompt building
│   └── main.py           # CLI version
└── output/               # Generated reports (ignored)
```

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
- Inspired by safe IT administration practices