# 🧠 NLP Inference Pipeline MVP  
**Sentiment Analysis with DistilBERT + BigQuery + Docker + CI/CD**

This project is an end-to-end MVP demonstrating cloud-based NLP inference, using Hugging Face's `transformers` pipeline (`DistilBERT`) to analyze sentiment of product reviews stored in BigQuery. The system is fully containerized, config-driven, and CI/CD-enabled—making it a production-adjacent showcase of modern ML deployment patterns.

---

## 🚀 Key Features

- **🔍 NLP Inference with DistilBERT**  
  Classifies product reviews as `POSITIVE` or `NEGATIVE` using a Hugging Face pipeline.

- **📡 BigQuery Integration**  
  Reads raw review data from BigQuery and writes back predictions—demonstrating a real-world, cloud-native inference loop.

- **🖥️ Local or Remote Execution Modes**  
  - Run locally using review data defined in `config.yaml`  
  - Or run against live BigQuery data using the Dockerized pipeline  
  Execution is managed via `entrypoint.py` with a `--mode` flag for flexibility.

- **🐳 Fully Containerized**  
  Dockerized with separate support for local development (`docker-compose.dev.yml`) and production deployment.

- **🛠 CI/CD with GitHub Actions**  
  On every push:
  - Builds and pushes the Docker image to Docker Hub
  - Mounts credentials securely via GitHub Secrets
  - Executes the actual inference pipeline in a GitHub-hosted container (not just a dummy test)

- **📁 Config-Driven Architecture**  
  Runtime behavior is controlled by `config/config.yaml` (e.g., dataset name, table name, row limits)—separating logic from environment.

---

## 📂 Project Structure

```
📦 NLP_Inference_MVP
├── src/
│   ├── bigquery_sentiment_pipeline.py        # Main inference logic
│   ├── entrypoint.py                         # Mode dispatcher (local vs BigQuery)
│   └── local_demo_nlp_sentiment_pipeline.py  # Local-only demo pipeline
├── config/
│   └── config.yaml                           # Controls dataset, table names, etc.
├── credentials/
│   └── your-key.json                         # GCP key (mounted at runtime)
├── .env                                      # Points to your key filename (not shown)
├── .github/workflows/
│   └── main.yml                              # CI/CD pipeline
├── Dockerfile
├── docker-compose.dev.yml
└── requirements.txt
```

---

## ⚙️ Usage

### 1. Local Development (No BigQuery)
```bash
# Load your .env file
export $(cat .env | xargs)

# Run locally using config.yaml review text
python src/entrypoint.py --task local
```

### 2. BigQuery Mode (Production-like)
```bash
# Uses the service account key to connect to BigQuery
python src/entrypoint.py --task bigquery
```

### 3. Docker (Dev)
```bash
docker-compose -f docker-compose.dev.yml up
```

---

## 🔐 Environment Variables

The `.env` file is **not shown here**, but expected to define:
```env
GOOGLE_CREDENTIALS_FILE=your-key-file.json
```

This tells Docker and CI/CD where to find the GCP service account key. The key itself is mounted under `/credentials/` inside the container, and .env is expected to be in the root directory.

---

## 🧪 How It Works (BigQuery Mode)

1. **Startup**: Authenticated BigQuery client is instantiated using credentials.
2. **Fetch**: Review data is pulled from a BigQuery table (e.g., `nlp_demo_reviews`).
3. **Inference**: Each review is processed by `transformers.pipeline("sentiment-analysis")`.
4. **Store**: Results (review ID, sentiment label, score, timestamp) are written back into a target BigQuery table.

---

## ✅ Skills & Stack Demonstrated

| Area               | Tools / Libraries |
|--------------------|-------------------|
| **NLP Inference**   | Hugging Face Transformers (DistilBERT) |
| **Cloud Access**    | Google Cloud BigQuery |
| **CI/CD**           | GitHub Actions + Docker Hub |
| **Secrets Mgmt**    | GitHub Secrets, .env, volume mounts |
| **Containerization**| Docker, docker-compose |
| **Code Practices**  | Config-driven logic, clean modular separation |

---

## 🔮 Future Enhancements

- **Self-Improving Feedback Loop (Planned)**  
  The pipeline is designed to support a future **feedback-driven retraining loop**, where predictions stored in BigQuery can be reviewed, corrected, or labeled over time—allowing for continuous model improvement.

  Instead of retraining on a nightly schedule (which risks overfitting and instability), the system will:
  - Log human or downstream feedback (e.g., `validated_label`, `is_mistake`)
  - Accumulate high-quality signals in a `fine_tune_buffer` table
  - Retrain the model **on a threshold basis** (e.g., 1,000+ validated examples)
  - Use Hugging Face's `Trainer` API with evaluation before replacing the current model
  - Automate deployment via the existing CI/CD flow

  This evolution would transition the system from a static inference pipeline to a **feedback-aware, self-correcting ML loop**, aligned with real-world MLOps maturity.

---

## 🧭 Potential Next Steps

- Add support for **batch inference** and parallel processing
- Introduce a **model registry** or checkpoint tracking
- Add basic **monitoring and alerting** for model confidence thresholds
- Plug into **Cloud Scheduler** or **Airflow** for managed runs

---

This project is designed to show not just technical implementation but real-world deployment readiness, CI/CD fluency, and architectural foresight for extending into adaptive, feedback-driven ML systems.