# ChemX: A Collection of Chemistry Datasets for Benchmarking Automated Information Extraction


## Abstract

Despite recent advances in machine learning, many scientific discoveries in chemistry still rely on manually curated datasets extracted from the scientific literature. Automation of information extraction in specialized chemistry domains has the potential to scale up machine learning applications and improve the quality of predictions, enabling data-driven scientific discoveries at a faster pace. In this paper, we present ChemX, a collection of 10 benchmarking datasets across several domains of chemistry providing a reliable basis for evaluating and fine-tuning automated information extraction methods. The datasets encompassing various properties of small molecules and nanomaterials have been manually extracted from peer-reviewed publications and systematically validated by domain experts through a cross-verification procedure allowing for identification and correction of errors at sources. In order to demonstrate the utility of the resulting datasets, we evaluate the extraction performance of the state-of-the-art large language models (LLMs). Moreover, we design our own agentic approach to take full control of the document preprocessing before LLM-based information extraction. Finally, we apply the recently emerged multi-agent systems specialized in chemistry to compare performance against the strong baselines. Our empirical results highlight persistent challenges in chemical information extraction, particularly in handling domain-specific terminology, complex tabular and schematic formats, and context-dependent ambiguities. We discuss the importance of expert data validation, the nuances of the evaluation pipeline, and the prospects of automated information extraction in chemistry. Finally, we provide open documentation including standardized schemas and provenance metadata, as well as the code and other materials to ensure reproducibility. ChemX is poised to advance automatic information extraction in chemistry by challenging the quality and generalization capabilities of existing methods, as well as providing insights into evaluation strategies.

## Links

- Datasets: [Hugging Face Dataset Collection](https://huggingface.co/collections/ai-chem/chemx-6820df9ecf568b1ff0ea2431)  
- Documentation: [ChemX Docs](https://ai-chem.github.io/ChemX/index.html)

## Code

Code for running baseline and agentic experiments is available in the [`LLM/`](./LLM) folder.

## Citation

Under review for NeurIPS 2025 Datasets and Benchmarks Track.

### The ChemX Ecosystem

This repository is the central hub for the ChemX project. The full ecosystem consists of several repositories designed to work together:

*   **[ChemX (this repository)](https://github.com/ai-chem/ChemX-RAG)**: Contains 10 datasets, documentation, and code for running baseline and agentic experiments for information extraction.
*   **[ChemX-dbt](https://github.com/ai-chem/ChemX-dbt)**: Contains database models (dbt) to use ChemX datasets and build ETL pipelines.
*   **[ChemX-backend](https://github.com/ai-chem/ChemX-backend)**: Contains backend code to serve ChemX datasets via API.
*   **[ChemX-RAG](https://github.com/ai-chem/ChemX-dbt)**: Contains code to build Retrieval-Augmented Generation (RAG) applications using ChemX datasets.
*   **[ChemX-client-python](https://github.com/ai-chem/ChemX-client-python)**: Contains a Python client for accessing ChemX datasets via the API.
