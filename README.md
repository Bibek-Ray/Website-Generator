# LLM Website Generator

Welcome to the **LLM Website Generator** — a baby-stage open-source project with a big dream:  
> To generate fully functional, styled websites using nothing but natural language prompts + the power of LLMs.

---

## What It Does

- Accepts plain English prompts like “Build me a portfolio for a creative writer”
- Uses **Gemini / Google Generative AI** to generate:
  - `index.html`
  - `styles.css`
- Streams the generated code to a frontend
- Offers a beautiful UI to input prompts and preview results
- Saves generated sites to disk (future: download as .zip or deploy via webhook?)

---

## Tech Stack

- **Backend**: FastAPI + Gemini (Google Generative AI)
- **Frontend**: HTML/CSS/JS (vanilla, clean and animated)
- **LLM Logic**: Modular agents for copywriting, code assembly, and styling
- **Infra**: Render (for deployment), dotenv for secrets

---

## Try It Locally

```bash
git clone https://github.com/yourusername/llm-website-generator.git
cd llm-website-generator
pip install -r requirements.txt
```

Make sure you set your **GEMINI_API_KEY** in a `.env` file like this:

```
GEMINI_API_KEY=your-google-api-key-here
```

Then run the server:

```bash
python app.py
```

Visit `http://localhost:8000` in your browser. Prompt it. Generate magic.

---

## Contributing

This project is in **very early development**, so **anything and everything is welcome**:
- Bug fixes
- Refactoring
- New ideas for prompt parsing or UI
- Export as `.zip` feature
- Real-time preview / live editing
- Deploy-to-Vercel/Netlify buttons
- Mobile responsiveness

**No contribution is too small.** Just open a PR or start a discussion!

---

## Roadmap (aka the Dream Board)

- [ ] Live preview pane beside prompt input
- [ ] In-browser code editor with save & export
- [ ] Theme selector (e.g., Minimal, Startup, Retro)
- [ ] Advanced agents for SEO + accessibility
- [ ] Zip download of generated site
- [ ] One-click deploy to GitHub Pages
- [ ] Mobile-first improvements

---

## License

[MIT](LICENSE) — Free to use, remix, build on, or turn into your own LLM-powered unicorn startup.

---

## Made by

Bibek Ray — and now, hopefully, **you** 💙  
Let’s build this into something wild together.
