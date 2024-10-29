# erotetic_explorer
Philosophy Dialetical Visualiser for Erotetic Theory Approach to Philosophising

Made by me with Claude's assitance

Implemented at: https://erotetic-explorer.onrender.com/

A web application that generates and visualizes dialectical trees of questions, responses, and objections using Flask, D3.js, and OpenAI's GPT API. The application creates dynamic, interactive visualizations inspired by Alexander Calder's mobile sculptures.

## Core Features

### 1. Dialectical Tree Generation
- Creates a structured tree of philosophical or general discourse
- Each node branches into multiple responses and objections
- Configurable depth (1-3 levels) and mode (philosophical/general)
- Maximum of 3 responses per node

### 2. Prompting Strategy
The application uses a three-tiered prompting approach:

1. **Initial Responses** (`async_get_responses`)
   - Prompts GPT to generate initial answers to the central question
   - Uses system prompt: "You are a helpful assistant that provides clear, concise responses"
   - Requests exactly 3 responses, each on a new line with dash prefix

2. **Objections** (`async_get_objections`)
   - Generates critical perspectives for each response
   - Uses system prompt: "You are a helpful assistant that provides critical analysis"
   - Maintains consistent format of 3 objections per response

3. **Counter-Responses** (`async_get_counter_responses`)
   - Creates counter-arguments to each objection
   - Uses system prompt: "You are a helpful assistant that provides thoughtful responses"
   - Follows same 3-item format pattern

### 3. Graph Structure

#### Node Types
- **Central Question (C)**: Root node of the tree
- **Responses (R1, R2, R3)**: First-level answers
- **Objections (R1O1, R1O2, etc.)**: Second-level critiques
- **Counter-responses (R1O1R1, R1O1R2, etc.)**: Third-level responses

#### Node ID System
- Uses hierarchical naming convention
- Example: `R1O2R3` means:
  - R1: First response to central question
  - O2: Second objection to that response
  - R3: Third counter-response to that objection

### 4. Visualization Features

#### Dynamic Rendering
- Calder-inspired organic shapes for nodes
- Color coding:
  - Central question: #1D3557 (dark blue)
  - Responses: #E63946 (red)
  - Objections: #457B9D (medium blue)

#### Interactive Elements
- Hover tooltips showing full node content
- Click-to-zoom functionality
- Draggable nodes
- Force-directed layout with:
  - Radial force arrangement
  - Collision detection
  - Mouse interaction influence
  - Continuous gentle movement

#### Animation
- Fluid shape morphing based on time
- Organic blob-like forms
- Shadow effects for depth
- Continuous animation frame updates

## Technical Implementation

### Backend (Flask)
```python
# Key configuration
MAX_ITEMS = 3  # Responses per node
GPT_MODEL = "gpt-4o-mini"  # OpenAI model selection
```

### Frontend
- D3.js for force simulation
- Force-Graph library for rendering
- Custom canvas rendering for Calder-inspired shapes
- Responsive design with mobile support

## Usage

1. Enter a question in the input field
2. Select depth (1-3) using the slider
3. Choose mode (philosophical/general)
4. Click "Generate" to create visualization
5. Interact with nodes to explore the dialectical tree

## User Interface
- Clean, minimal design
- Font: Archivo (Google Fonts)
- Responsive controls
- Interactive depth slider
- Mode toggle between philosophical and general approaches

The application creates an engaging way to explore complex questions through a structured dialectical approach, with visual elements inspired by Calder's kinetic art style.
