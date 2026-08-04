# Project Instructions

Instructions for the AI agent working in this Business Central project. Loaded automatically at session start.

## Project Info

- **BC Version:** per task era (BC 24.0-27.2 — this repo hosts the Microsoft Base Application and first-party apps)
- **Deployment:** SaaS
- **Object ID Range:** Microsoft base-application ranges (change existing objects; do not allocate new object ID ranges)
- **Mandatory Affixes:** none
- **Publisher:** Microsoft

## Plugin

This project uses **al-dev-toolkit**. The plugin injects its command routing map at session start, and `.github/instructions/al-workflow.instructions.md` guards AL edits. Route all BC work through plugin commands — they own the coding conventions (DataClassification, Labels, SetLoadFields, affix, CodeCop). Ask `/al-help` for the command catalog.

### Paths

- Plans: `.github/plans/`
- Context files the user adds for a task: `.github/context/`

## Project-Specific Rules

- Focus all work on the W1 (Worldwide) layer; do not touch country/region localizations unless explicitly requested.
