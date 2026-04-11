# Diagram Types - Detailed Reference

## 1. Logical Flow Diagram

Shows the logical flow of data or processes through system components.

**Key elements:**
- Actors/Users (orange)
- Services/Processes (blue)
- Data Stores (cyan)
- External Systems (purple)
- Data flows (solid arrows)

**Example structure:**
```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────▶│ Service │────▶│  Data   │
└─────────┘     └─────────┘     └─────────┘
```

## 2. Logical Architecture Diagram

Abstract representation of system components without cloud provider specifics.

**Typical layers:**
- Presentation Layer (UI, Web, Mobile)
- Application Layer (API Gateway, Business Logic)
- Data Layer (Database, Cache)

**Example structure:**
```
┌─────────────────────────────────────────┐
│            Presentation Layer            │
│  ┌─────────────┐  ┌─────────────┐       │
│  │  Web UI     │  │  Mobile    │       │
│  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│            Application Layer             │
│  ┌─────────────┐  ┌─────────────┐       │
│  │   API       │  │  Business   │       │
│  │   Gateway   │  │   Logic     │       │
│  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│              Data Layer                  │
│  ┌─────────────┐  ┌─────────────┐       │
│  │  Database   │  │    Cache    │       │
│  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────┘
```

## 3. BPMN Process Diagram

Business process modeling using standard BPMN symbols.

| Symbol | Shape | Meaning |
|--------|-------|---------|
| Start Event | Circle (green border) | Process start point |
| End Event | Circle (red border) | Process end point |
| Activity/Task | Rounded Rectangle | Work to be performed |
| Gateway/Decision | Diamond | Branching based on conditions |
| Sequence Flow | Solid arrow | Order of activities |

## 4. UML Sequence Diagram

Shows interaction between components over time.

**Structure:**
- Vertical lifelines for each component
- Horizontal arrows for messages
- Time flows downward
- Activation bars show when a component is active

**Example:**
```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  Actor  │     │Service A│     │Service B│
└────┬────┘     └────┬────┘     └────┬────┘
     │              │              │
     │─────────────▶│              │
     │              │─────────────▶│
     │              │◀─────────────│
     │◀─────────────│              │
```

## 5. Data Flow Diagram (DFD)

Shows system data movement and transformation.

**Components:**
- **External Entity** (square) - Sources/destinations outside system
- **Process** (circle/rounded rectangle) - Data transformation
- **Data Store** (open-ended rectangle) - Data storage
- **Data Flow** (arrow) - Movement of data

**Levels:**
- Context Diagram (Level 0) - Shows system as one process
- Level 1 DFD - Major processes and data flows
- Level 2+ DFD - Decompose complex processes

## 6. Decision Flowchart

Visualizes branching logic and decision points.

**Elements:**
- Start/End points (ovals)
- Process steps (rectangles)
- Decision points (diamonds)
- Connectors with labels (Yes/No)
- Error handling paths (red)

## 7. System Interaction Diagram

Shows how different systems or components interact.

**Focus:**
- API calls and responses
- Event flows
- Message passing
- Synchronous vs asynchronous interactions

## Choosing the Right Diagram Type

| Need | Best Diagram Type |
|------|-------------------|
| Show data flow through system | Logical Flow Diagram |
| Show system structure | Logical Architecture Diagram |
| Document business process | BPMN Process Diagram |
| Show component interactions over time | UML Sequence Diagram |
| Analyze data movement | Data Flow Diagram (DFD) |
| Visualize decision logic | Decision Flowchart |
| Show system-to-system communication | System Interaction Diagram |
