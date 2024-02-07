# datapipe-examples

This repository contains a collection of examples demonstrating the usage of Datapipe (https://github.com/epoch8/datapipe), a real-time, incremental ETL library for Python. Our examples aim to provide practical, easy-to-understand demonstrations of how datapipe can be integrated into various data processing workflows.

## About Datapipe

[Datapipe](https://datapipe.dev/) is a real-time, incremental ETL library for Python with record-level dependency tracking.

Datapipe is designed to streamline the creation of data processing pipelines. It excels in scenarios where data is continuously changing, requiring pipelines to adapt and process only the modified data efficiently. This library tracks dependencies for each record in the pipeline, ensuring minimal and efficient data processing.

https://datapipe.dev/

## Key Features:

- Incremental Processing: datapipe processes only new or modified data, significantly reducing computation time and resource usage.
- Real-time ETL: The library supports real-time data extraction, transformation, and loading.
- Dependency Tracking: Automatic tracking of data dependencies and processing states.
- Python Integration: Seamlessly integrates with Python applications, offering a Pythonic way to describe data pipelines.

## Getting Started
For those familiar with Poetry, setting up and running the datapipe-examples is straightforward:

1. Clone the Repository: Begin by cloning the datapipe-examples repository from GitHub.
2. Navigate to an Example: Select and navigate to the directory of the example you're interested in.
3. Install Dependencies with Poetry: run 'poetry install' in the chosen example directory to install the required dependencies.

## Contribution
Contributions to this repository are welcome! If you have an interesting use case or example of datapipe that you'd like to share, please feel free to open a pull request.

## Support and Community
Issue Reporting: If you encounter issues or bugs, please report them via the repository's Issues section.
