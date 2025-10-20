# Grade 7 Science Tutor (Streamlit + OpenAI Assistants)

An interactive tutor app that uses the OpenAI **Assistants API** with **File Search** to teach Grade 7 Science.

## 1) Prerequisites
- Python 3.10+
- An OpenAI API key: https://platform.openai.com/
- An existing Assistant (with File Search on) in the OpenAI dashboard.

> Note: OpenAI has **deprecated** the Assistants API in favor of the **Responses API** and plans shutdown in 2026. This app works now; see "Migration" below.  
> Docs: Deprecation + dates and migration guidance.  
> - Deprecations overview: https://platform.openai.com/docs/deprecations/incremental-model-updates  
> - Assistants deep-dive (deprecated) with migration notes: https://platform.openai.com/docs/assistants/deep-dive/max-completion-and-max-prompt-tokens

## 2) Setup
```bash
git clone https://github.com/<your-username>/grade7-science-tutor.git
cd grade7-science-tutor
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your OPENAI_API_KEY and ASSISTANT_ID
