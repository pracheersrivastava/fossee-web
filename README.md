# CHEM•VIZ - FOSSEE Scientific Analytics UI

Chemical Equipment Parameter Visualizer built with React (Web) and PyQt5 (Desktop).

## Design System

All UI implementations follow the specifications in [`design.md`](design.md) exactly. The design system enforces:

- **Data First**: UI never competes with charts or tables
- **Academic Neutrality**: No flashy gradients or marketing-style visuals
- **Predictable Interactions**: One primary action per screen
- **Cross-Platform Parity**: Visual match between React and PyQt5

## Project Structure

```
├── design.md              # Design system specification
├── src/                   # React web application
│   ├── components/
│   │   ├── Layout/        # Header, Sidebar, MainContent
│   │   └── CSVUpload/     # CSV upload with summary card
│   ├── styles/
│   │   ├── tokens.css     # Design tokens as CSS variables
│   │   └── global.css     # Reset, typography, utilities
│   ├── App.jsx
│   └── index.jsx
└── desktop/               # PyQt5 desktop application
    ├── core/
    │   └── tokens.py      # Design tokens as Python constants
    ├── styles/
    │   └── theme.qss      # QSS stylesheet
    ├── widgets/           # Header, Sidebar, MainContent
    ├── main_window.py
    └── app.py
```

## Quick Start

### Web (React)

```bash
npm install
npm run dev
```

### Desktop (PyQt5)

```bash
cd desktop
pip install -r requirements.txt
python app.py
```

## Design Tokens

| Category | Web | Desktop |
|----------|-----|---------|
| Colors | CSS variables | Python constants |
| Typography | Inter | Source Sans 3 |
| Spacing | 8px base unit | 8px base unit |
| Shadows | CSS | QSS |

## License

FOSSEE Project, IIT Bombay
