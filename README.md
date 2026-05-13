# Worklog

A desktop worklog app with AI-powered summaries and end-of-year self-review generation, built with Python, CustomTkinter, and the Claude API.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-green) ![Claude](https://img.shields.io/badge/AI-Claude%20Opus%204.7-purple)

## Features

- **Log daily work** with date, title, notes, project, and category
- **Filter entries** by date range or project
- **Summarize any period** — AI generates a narrative summary of selected entries
- **Annual review generator** — one click produces a structured self-review ready to share with your manager
- **Streaming AI output** — responses appear in real time as Claude writes them
- **Local SQLite storage** — all data stays on your machine at `~/.worklog/worklog.db`

## Setup

### 1. Install dependencies

```bash
pip install customtkinter anthropic
```

### 2. Get an Anthropic API key

Sign up at [console.anthropic.com](https://console.anthropic.com), create an API key, and export it:

```bash
# Temporary (current session only)
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export ANTHROPIC_API_KEY=sk-ant-your-key-here' >> ~/.bashrc
source ~/.bashrc
```

### 3. Launch

```bash
python ~/worklog/main.py
```

## Usage

### Adding entries

Click **+ New Entry** and fill in:
- **Date** — defaults to today
- **Title** — short description of what you worked on
- **Project** — optional, used for filtering and grouping in reviews
- **Category** — Bug Fix, Feature, Code Review, Meeting, etc.
- **Notes** — detailed description

### Filtering

Use the left panel to filter by date range or project. The entry list updates immediately.

### AI Summarization

- **Summarize Period** — summarizes whatever entries are currently visible (respects active filters)
- **Annual Review** — enter a year and generate a full structured self-review with sections for accomplishments, technical growth, collaboration, and impact

The AI summary window streams output live and includes a **Copy** button to paste the result into a doc or email.

## Project Structure

```
worklog/
├── main.py              # Entry point
├── database.py          # SQLite layer (~/.worklog/worklog.db)
├── ai_summary.py        # Claude API integration (streaming)
├── ui/
│   ├── app.py           # Main window
│   ├── entry_form.py    # Add/edit entry dialog
│   └── summary_dialog.py  # AI summary window
└── requirements.txt
```

## Annual Review Output Format

The annual review is structured for use directly in a performance review conversation:

1. **Executive Summary**
2. **Key Accomplishments** (grouped by project/area)
3. **Technical Growth**
4. **Collaboration & Leadership**
5. **Impact & Results**
6. **Looking Ahead**
