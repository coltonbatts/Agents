# AGENTS

A minimalist, retro-inspired framework for building specialized AI agents that combine form and function.

## Features

- **Modular Agent Architecture**: Easily create and combine specialized agents
- **Built-in Agents**:
  - Data Agent: Handle CSV, JSON, SQLite, and YAML data
  - API Agent: Integrate with external services
  - Analysis Agent: ML/AI capabilities using state-of-the-art models
  - Text Processor: Basic text processing and analysis
- **Web Interface**: Clean, retro-inspired UI for managing agents
- **CLI Tools**: Powerful command-line interface for workflow management
- **Scheduling**: Cron-based task scheduling

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/<USERNAME>/AGENTS.git
cd AGENTS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the web interface:
```bash
python run_web.py
```

4. Use the CLI:
```bash
./agents.py --help
```

## Project Structure

- `core/`: Core agent framework and utilities
- `agents/`: Specialized agent implementations
- `web/`: Web interface and API
- `cli/`: Command-line interface tools
- `examples/`: Sample workflows and usage examples

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest
```

## Deployment

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
vercel --prod
```

The project is configured for serverless deployment on Vercel with:
- FastAPI backend using Python runtime
- Static file serving
- WebSocket support (where available)

## Environment Variables

Create a `.env` file with:
```
OPENAI_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
```

## License

MIT License - see LICENSE file for details
