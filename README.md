# 🎯 LeadScout — Autonomous B2B Lead Research & Outreach Agent

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful-orange.svg)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io/)
[![Gemini](https://img.shields.io/badge/Google-Gemini-purple.svg)](https://ai.google.dev/)

**LeadScout** is a production-grade, stateful multi-agent system designed to automate B2B prospect research, company intelligence synthesis, and hyper-personalized cold outreach generation. Built with a robust **Human-in-the-Loop (HITL)** review loop, it combines probabilistic LLM generation with deterministic tool execution and database persistence.

---

## 🏗️ System Architecture & Workflow

Unlike basic linear LLM scripts, LeadScout models outbound sales outreach as a **stateful directed graph (DAG)** with cyclical routing for iterative revisions:

```text
 ┌─────────┐      ┌────────────┐      ┌─────────────┐      ┌──────────────┐
 │  Start  │ ───> │  Research  │ ───> │  Synthesize │ ───> │  Write Email │
 └─────────┘      └────────────┘      └─────────────┘      └──────────────┘
                                                                  │
                                                                  ▼
                                                      ┌──────────────────────┐
   ┌─────────┐      ┌─────────────┐                   │    Human Review      │
   │   CRM   │ <─── │   Approve   │ <──────────────── │   (Interrupt Check)  │
   │ Logger  │      │   & Send    │                   └──────────────────────┘
   └─────────┘      └─────────────┘                              │
                         ▲                                       │
                         │                   ┌───────────────────┴───────────────────┐
                         │                   ▼                                       ▼
                         │          *(Edit Requested)*                      *(Rejected)*
                         │                   │                                       │
                         └───────────────────┘                                       ▼
                                          │                              [Terminate Workflow]
                                     (Loop Back)
