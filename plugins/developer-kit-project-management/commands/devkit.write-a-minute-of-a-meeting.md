---
description: Generates professional meeting minutes from transcripts or notes. Use when you need to create structured meeting documentation after a meeting.
argument-hint: "[transcript-file] [meeting-title] [date]"
allowed-tools: Read, Write
---

Act as an expert administrative assistant specialized in creating meeting minutes. Analyze the provided transcript or notes and produce a clear, concise, and professional meeting minute document.

## Input

Read the meeting transcript from: **$1**

## Meeting Information Template

Use these details or ask for them if not provided:
- **Meeting Title/Subject:** $2
- **Date and Time:** $3
- **Location/Platform:** (e.g., Teams, Zoom, in-person)
- **Attendees:** (list participants)
- **Meeting Objective:** (purpose of the meeting)

## Document Structure

Create the meeting minutes with the following sections:

### 1. Executive Summary
Begin with a brief paragraph (3-4 sentences maximum) summarizing the main outcomes and key decisions from the meeting.

### 2. Agenda Items Discussed
For each agenda item, create a dedicated section that includes:
- Clear and concise summary of the discussion
- Significant contributions from participants, properly attributed
- Conclusions reached for each item

### 3. Decisions Made
Extract and list all final decisions approved during the meeting. For each decision, specify:
- The decision itself
- Who proposed/approved the decision

### 4. Action Items
Create a table with the following columns:

| Action | Responsible | Deadline |
|--------|------------|----------|
| Description of the task | Person or team assigned | Completion date |

### 5. Open Issues/Next Steps
List any unresolved issues or topics to be discussed in future meetings.

### 6. Next Meeting
Include date and time of the next meeting if established.

## Style Guidelines

- Use professional, clear, and objective language
- Avoid unnecessary jargon and unexplained acronyms
- Use bullet points to improve readability
- Maintain a neutral and factual tone
- Format using proper Markdown syntax

## Execution Instructions

**Agent Selection**: To execute this task, use the following approach:
- Primary: Use `general-purpose` agent with appropriate domain expertise
- Or use specialized agent if available for the specific task type
