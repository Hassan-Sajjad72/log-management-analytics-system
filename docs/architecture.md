# System Architecture

## Overview

The system has three main layers:

1. PostgreSQL database layer
2. Flask backend layer
3. HTML/Jinja dashboard layer

## Data Flow

```text
Synthetic Log Generator
        ↓
PostgreSQL Database
        ↓
Advanced DB Techniques
        ↓
Flask Backend
        ↓
Dashboard Pages and JSON APIs