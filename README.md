# AI Pipeline Incident Agent 🤖

An agentic AI tool that monitors Apache Airflow pipelines, 
diagnoses failures using LLM reasoning, and recommends 
or executes remediation actions — reducing manual 
on-call toil for data engineering teams.

## Problem Statement
Data engineering teams spend significant time 
diagnosing pipeline failures manually — parsing 
Airflow logs, cross-referencing past incidents, 
and deciding on fixes. This agent automates that 
entire workflow.

## Architecture
Airflow REST API → LangChain Agent → Vector DB (past incidents)
↓
Diagnosis + Recommendation
↓
Slack Alert / Auto-retry / Jira Ticket

## Tech Stack
- **Orchestration:** Apache Airflow
- **Agent Framework:** LangChain + LangGraph
- **LLM:** Claude API (claude-sonnet-4-20250514)
- **Vector Database:** ChromaDB
- **API Layer:** FastAPI
- **Cloud:** AWS (S3, EC2, Redshift)
- **Notifications:** Slack API
- **CI/CD:** GitHub Actions

## Features (In Progress)
- [x] Project architecture designed
- [ ] Airflow REST API integration
- [ ] LangChain agent with diagnosis tools
- [ ] ChromaDB vector store for past incidents
- [ ] RAG pipeline for historical incident retrieval
- [ ] Slack notification integration
- [ ] Auto-retry with human approval gate
- [ ] FastAPI wrapper for agent endpoints

## Use Cases
1. **Failure Diagnosis** — Agent reads Airflow logs 
   and explains root cause in plain English
2. **Historical Matching** — Retrieves similar past 
   incidents from vector DB to inform fix
3. **Auto-remediation** — Triggers DAG retry or 
   creates Jira ticket with one approval click
4. **Natural Language Queries** — On-call engineer 
   asks "what failed last night?" and gets a 
   structured summary

## Project Status
🚧 Active development — building incrementally 
alongside production data engineering work.

## Author
Sridevi Penmetsa — Senior Data Engineer
[LinkedIn](https://www.linkedin.com/in/sridevi-penmetsa-0b4562a3)
