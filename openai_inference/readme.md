# Cost-Effective GPT API Usage with Datapipe

## Overview
This directory presents an example that demonstrates how to use Datapipe for cost-effective interaction with the OpenAI GPT API.

Imagine you have a task to engineer the most effective prompt to process all the examples. Developing an effective prompt is an ongoing task: we continually add new test examples and tweak the prompt to get better results.

The primary objective is to process "prompt + example" pairings efficiently, ensuring that each pairing is processed exactly once to avoid unnecessary expenses associated with redundant API requests.

## Description
This example illustrates a real-world scenario where managing and tracking the processing of large datasets with an AI model is crucial. The focus is on:

- Minimizing Costs: By ensuring that each data pairing is processed only once.
- Efficient Data Tracking: Automatically identifying which examples have been processed with each specific prompt and tracking their results.

## Challenges Addressed

- New Data Addition: Process only new examples added to the dataset.
- Data Modification: Re-process examples if they undergo any changes.
- Prompt Changes: Re-process all examples when a prompt is changed or a new prompt is added.
- Deletion Handling: Remove processing results if an example or a prompt is deleted.

## Solution with Datapipe

Using Datapipe open-source library, this example demonstrates:

- Automatic Tracking: datapipe tracks completed computations and recalculates only for updated data.
- Simplified Developer Workflow: Developers can focus on writing Python functions without worrying about the complexity of tracking computation status.

## Prerequisites

- Python 3.x
- Poetry for dependency management

## Setup

1. Clone this repository.
2. Navigate to this directory.
3. Install dependencies using Poetry (poetry install)
4. Set your OpenAI API key in the script.

## Usage
To run the example:
1. Create all nesessary SQLite databases by running
```
datapipe db create-all
```
2. Run the data processing
```
datapipe run
```

Datapipe retrieves all examples from the 'examples' table in the data.sqlite database and processes them using the OpenAI API, guided by the prompts in the 'prompts' table. The results of this processing are then stored in the 'output' table.

Now, you can add, modify, or delete prompts and examples in the database. Observe how Datapipe efficiently tracks these changes, processing only the newly added, modified, or deleted data, ensuring an optimized and targeted approach to data handling.
