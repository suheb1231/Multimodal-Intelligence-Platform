
## 🎥 Project Demo Video

Watch the complete 10-minute demonstration of the Multimodal Intelligence Platform.

[▶ Watch Project Demo Video](https://drive.google.com/file/d/1rvWovgLIXdrYLqZDGo7OZdgNJ69nS9Xd/view?usp=sharing)

## 🚀 Live Application

[🌐 Open Multimodal Intelligence Platform](https://multimodal-ai-platform.streamlit.app/)


# Coursera: Multimodal Intelligence Platform

An AI-powered learning intelligence platform designed to process, organize, retrieve, and analyze educational content across multiple data formats. The project combines multimodal preprocessing, embeddings, retrieval-augmented generation (RAG), evidence management, analytics, and recommendation components into a unified Streamlit application.

## 1. Project Overview

Educational content is often distributed across different formats, including PDF documents, text files, images, audio, video, quizzes, and discussion data. Working with these resources separately can make it difficult to search for relevant information and understand learning activity.

The **Multimodal Intelligence Platform** aims to provide a unified workflow for handling educational assets, extracting useful information, retrieving relevant evidence, and presenting learning-related insights through an interactive application.

## 2. Project Objectives

- Support the intake and organization of different educational asset types.
- Process and extract information from supported content formats.
- Generate and manage text and image embeddings.
- Store and retrieve relevant information using vector-based retrieval.
- Support evidence-based question answering through a RAG workflow.
- Identify potential learning friction and generate recommendations.
- Provide analytics and review capabilities through the application.

## 3. Key Modules

The project is organized into modular components:

| Module | Responsibility |
|---|---|
| Asset Ingestion | File validation and asset registration |
| Preprocessing | Content extraction and processing |
| Embeddings | Text and image representation |
| Database | Vector database management |
| Retrieval | Query processing and evidence retrieval |
| RAG | Answer generation and prompt management |
| Agents | Asset profiling, quality validation, retrieval planning, and synthesis |
| Recommendations | Learning-friction detection |
| Review | Evidence and review management |
| Analytics | Learning and operational analytics |
| Dashboard | Application dashboard and user interface |

*The availability and completeness of individual features depend on their implementation in the current source code.*

## 4. Project Architecture

The platform follows a modular processing and retrieval architecture.

```text
                  EDUCATIONAL ASSETS
                          |
                          v
                  ASSET INGESTION
                          |
                          v
                    PREPROCESSING
                          |
                          v
                CONTENT REPRESENTATION
                          |
                          v
                     EMBEDDINGS
                          |
                          v
                  VECTOR DATABASE
                          |
                          v
                  RETRIEVAL SYSTEM
                          |
                          v
                   RAG COMPONENTS
                          |
             +------------+------------+
             |            |            |
             v            v            v
          ANSWERS     RECOMMENDATIONS  REVIEW
             |            |            |
             +------------+------------+
                          |
                          v
                  STREAMLIT APP
                          |
                          v
                     ANALYTICS
```

## 5. Technology Stack

The project uses the following technologies and libraries, subject to the dependencies configured in `requirements.txt`:

- **Python** – Core programming language
- **Streamlit** – Application interface
- **Pandas** – Data handling and analysis
- **LangChain** – RAG and language-model integration
- **FAISS / Vector Database** – Vector-based retrieval
- **Sentence Transformers** – Embedding generation
- **OpenCV** – Image and video processing
- **PyMuPDF** – PDF processing
- **Pillow** – Image handling
- **Plotly** – Interactive visualizations

## 6. Repository Structure

```text
Coursera-Multimodal-Intelligence-Platform/
│
├── agents/
│   ├── asset_profiler.py
│   ├── quality_validator.py
│   ├── retrieval_planner.py
│   └── synthesis_writer.py
│
├── dashboard/
│
├── database/
│   └── chroma_manager.py
│
├── embeddings/
│   ├── image_embeddings.py
│   └── text_embeddings.py
│
├── ingestion/
│   ├── asset_registry.py
│   └── file_validator.py
│
├── preprocessing/
│   ├── audio_processor.py
│   ├── image_processor.py
│   ├── pdf_processor.py
│   ├── text_processor.py
│   ├── transcript_processor.py
│   ├── video_processor.py
│   └── ...
│
├── rag/
│   ├── answer_generator.py
│   ├── assistant.py
│   ├── embedding_generator.py
│   ├── prompt_templates.py
│   └── vector_store.py
│
├── recommendations/
│   └── friction_detector.py
│
├── retrieval/
│   ├── evidence_ranker.py
│   ├── evidence_retriever.py
│   └── query_processor.py
│
├── review/
│   └── review_manager.py
│
├── data/                  # Runtime and generated data
│
├── analytics.py
├── app.py
├── cleanup.py
├── config.py
├── pipeline.py
├── study_tools.py
├── requirements.txt
├── packages.txt
├── .gitignore
└── README.md
```

## 7. Installation and Setup

### Prerequisites

- Python installed on your system
- Git
- A compatible environment for the dependencies listed in `requirements.txt`

### Step 1: Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Coursera-Multimodal-Intelligence-Platform
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### Step 2: Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file in the project root if the application requires environment variables.

Example template:

```env
# Add the environment variable names required by config.py.
# Keep all API keys and credentials private.
```

Use the variable names expected by the actual application configuration. Never upload API keys, passwords, or private credentials to GitHub.

### Step 5: Run the application

```powershell
streamlit run app.py
```

Streamlit will provide a local URL in the terminal. Open that URL in your browser.

## 8. Running the Application

The main application entry point is:

```text
app.py
```

The supporting modules are organized by responsibility so that ingestion, preprocessing, retrieval, RAG, recommendations, review, and analytics logic can be maintained independently.

For processing workflows, refer to:

```text
pipeline.py
```

For configuration, refer to:

```text
config.py
```

## 9. Data and File Management

The `data/` directory is used for application data and generated processing outputs.

Depending on the workflow, it may contain:

- Uploaded educational assets
- Processed content
- Extracted metadata
- Transcripts and extracted text
- Generated learning resources
- Vector database files
- Application records

Generated data and local runtime files should not be committed to the source repository unless they are intentionally included as documented sample data.

## 10. Security and Configuration

Security is an important part of this project.

- API keys must be stored in environment variables or the deployment platform's secret manager.
- The `.env` file must remain excluded from Git.
- Private credentials must never be included in source code.
- Generated user data and local databases should be excluded from public commits unless explicitly required.
- Deployment secrets should be configured through the hosting platform.

Before pushing changes, verify the repository:

```powershell
git status
```

## 11. Deployment

The application is built with Streamlit and can be prepared for deployment on a compatible Streamlit hosting environment.

Deployment preparation should include:

1. Confirming that all dependencies are listed in `requirements.txt`.
2. Configuring required system packages.
3. Adding environment variables through the hosting platform's secrets settings.
4. Verifying that generated local data is not required for a fresh deployment.
5. Testing the deployed application with representative sample assets.

The repository includes `packages.txt` for system-level package configuration where supported by the hosting platform.

## 12. Testing and Verification

Before submitting or deploying the project, verify the following:

- The application starts successfully.
- Supported asset types pass their ingestion and validation workflows.
- Preprocessing modules handle their expected input formats.
- Embedding and retrieval components work with available test data.
- RAG components handle queries and available evidence correctly.
- Analytics and review components load without errors.
- Required environment variables are configured.
- No private credentials or unnecessary generated files are committed.

## 13. Current Scope and Limitations

The project is an evolving implementation. Actual functionality depends on the available modules, configured models, external services, and runtime environment.

Potential limitations include:

- Processing time may vary depending on asset size and format.
- Some AI-generation capabilities may depend on model availability and API limits.
- OCR, audio transcription, and video processing may require additional system packages.
- Results depend on the quality of source content and extracted information.
- A fresh deployment may require separate configuration of secrets and system dependencies.

## 14. Future Improvements

Possible areas for further development include:

- Improved multimodal retrieval and evidence alignment.
- More comprehensive learning analytics.
- Enhanced recommendation evaluation.
- Better processing-status monitoring.
- Additional automated testing.
- Improved deployment reliability and error handling.
- Expanded support for educational content formats.

## 15. Author and Project Information

**Project:** Coursera – Multimodal Intelligence Platform  
**Category:** Artificial Intelligence / Generative AI / Multimodal Systems  
**Application Framework:** Streamlit  
**Primary Language:** Python

---

**Note:** This README describes the repository structure and intended system architecture. Feature descriptions should be updated whenever implementation details change.
