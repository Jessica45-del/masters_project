# Multi-Agent Diagnostic Reasoning using Large Language Models for Rare Disease Diagnosis

## Overview
This project explores the use of LLM agents for autonomous reasoning in rare disease diagnosis. By leveraging structured input in the form of Human Phenotype Ontology (HPO) terms, the system performs disease prioritization and is benchmarked against Exomiser using the PhEval framework.

## Installation

Clone the masters_project repo and create a poetry environment to install dependencies
```
git clone https://github.com/Jessica45-del/masters_project.git

cd masters_project

poetry shell

poetry install
```

## Run Command

```
pheval run -i /path/to/input_dir -t /path/to/testdatadir -r agentphevalrunner -o /path/to/resultsdir

input_dir - path to location of config.yaml file

testdata-dir - path to phenopackets directory

agentphevalrunner - custom runner name

results_dir - path to results directory
```



