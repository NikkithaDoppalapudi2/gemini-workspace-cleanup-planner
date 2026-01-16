# 🛡️ Workspace Insights Pro

**Workspace Insights Pro** is a premium, enterprise-grade AI-assisted platform for auditing Google Workspace user data and optimizing license management. Built for security-conscious IT administrators, it leverages Google's Gemini AI to provide actionable intelligence without compromising control.

## 🚀 Key Features

### 🏢 Enterprise Identity
- **Professional UI**: A sleek, dark-mode 'Glassmorphism' interface designed for executive presentations.
- **Custom Branding**: Fully rebranded with a corporate identity and professional iconography.
- **Zero Emoji Policy**: Clean, professional layout suitable for corporate environments.

### 🧠 Intelligence Engine
- **AI Classification**: Categorizes users into Safe, Pending, or Decommissioning targets.
- **API Rotation**: Automatically switches between Gemini 1.5 Flash and Pro models to ensure 100% uptime.
- **Batch Processing**: Securely handles datasets of any size with optimized vector batching.

### 📊 Analytics & Reporting
- **Security Dashboard**: Visualizes risk distribution, privilege levels, and organizational roles.
- **Risk Score Attribution**: Algorithmic scoring based on activity gaps, access scalars, and persona types.
- **Multi-Format Export**: One-click generation of Executive Excel sheets and Compliance PDF reports.

### 📧 Communication Strategy
- **Notification Engine**: Generates professional outreach templates for managers and stakeholders.
- **Bulk Outreach**: Consolidates review requests to maximize response rates and minimize noise.

## 🛠️ System Overview

### Risk Scoring Methodology
| Score | Classification | Operational Response |
|-------|----------------|----------------------|
| 0-30 | 🟢 Standard | Baseline monitoring |
| 31-60 | 🟡 Advisory | Quarterly validation |
| 61-80 | 🟠 Elevated | Immediate verification |
| 81+ | 🔴 Critical | Priority administrative review |

### Project Architecture
```
workspace-insights-pro/
├── app.py                     # Professional UI (6 Intelligence Modules)
├── src/
│   ├── gemini_client.py      # Multi-model rotation & retry logic
│   ├── risk_calculator.py    # Algorithmic scoring engine
│   ├── email_templates.py    # Corporate communication generator
│   └── export_utils.py       # PDF/Excel report generators
├── assets/
│   └── logo.png              # Corporate brand identity
└── prompts/
    └── cleanup_prompt.txt    # Intelligence classification logic
```

## 🚥 Quick Start

1. **Clone & Setup**:
   ```bash
   git clone https://github.com/NikkithaDoppalapudi2/gemini-workspace-cleanup-planner.git
   cd gemini-workspace-cleanup-planner
   pip install -r requirements.txt
   ```

2. **Configure API**:
   Create a `.env` file with your Gemini API key:
   ```env
   GEMINI_API_KEY=your_key_here
   ```

3. **Launch Platform**:
   ```bash
   streamlit run app.py
   ```

## 🛡️ Trust & Safety
This platform operates on a **Human-in-the-Loop** model. It identifies, categorizes, and organizes, but **never deletes** or modifies access directly. All administrative actions must be performed through the official Google Workspace Admin Console.

## 📄 License
Licensed under the MIT License.

---
*Powered by Workspace Insights Intelligent Analysis Engine.*