# Renue

### Automated Continuing Education Tracker & License Renewal Assistant

<p align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" />
  <br />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI" />
</p>
<p align="center">

> **Renue** is a full-stack Chrome Extension that automates the tedious process of tracking Continuing Education (CE) credits. It uses AI to extract data from pdfs, and injects that data directly into online renewal forms.

---

## Demo

[Placeholder]

---

## The Problem

Insurance sales representatives are required to complete 30 hours of continuing education training every two years. Currently this process involves:

1. Manually parsing dozens of PDF certificates.
2. Entering data into a spreadsheet to track hours.
3. Re-typing that same data into provincial renewal forms one by one.

**The Solution** Renue acts as a digital wallet for CE certificates by automatically parsing cretificates via OCR/LLM and autofilling government forms with a single click.

---

## The Architecture

Renue utilizes a decoupled headless architecture to ensure the extension remains lightweight while offloading heavy data processing to a dedicated server.

1. **Client (Extension):** Operates as a UI layer. It captures the user's drag-and-drop event and converts the file to a byte stream.
2. **API Gateway:** A Python (FastAPI) server receives the stream. It utilizes a layered Service-Repository pattern to seperate business logic from database access.
3. **Processing Pipeline:**\
    **Step 1:** PyPDF extracts raw text from the file stream.\
    **Step 2:** Text is sent to an LLM (OpenAI) with a strict JSON-schema prompt to extract structured data (Course, Provider, Date, Credits).

4. **Data Storage:** Confirmed data is stored in PostgreSQL database (Supabase) with Row Level Security (RLS) enabled to ensure user data isolation.

[Placeholder for Diagram]

---

## Key Features

- **Drag-and-Drop Parsing:** Dragging a PDF certificate into the extension window automatically parses and extracts the data required for license renewal.
  - _Implementation:_ Sends file byte stream to Python backend, parse raw text, and uses OpenAI to extract "Course Provider", "Course Name", "Date", and "Credits" from unstructured text.

- **Visual Progress Dashboard:** A real time progress bar indicating credit hours obtained for the current renewal cycle.
  - _Implementation:_ React state management calculates totals from PostgreSQL database.

- **One-Click From Autofill:** Continuing education credit information is automatically injected into official license renewal form.
  - _Implementation:_ Content Scripts detect the target renewal URL and inject database records directly into the DOM input fields.

---

## Challenges & Learnings

[Placeholder]

---

## Running Locally

[Placeholder]
