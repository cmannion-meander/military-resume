# Military Transition Support App

Welcome to the Military Transition Support App! This application is designed to assist military personnel transitioning to civilian life by providing various tools and resources.

Access the live version here: https://military-resume.azurewebsites.net/

## Getting Started

To get started with the Military Transition Support App, follow these steps:

### Installation

1. Clone the repository to your local machine:

    ```
    git clone https://github.com/cmannion-meander/military-resume.git
    ```

2. Navigate to the project directory:

    ```
    cd military-resume
    ```

3. Install the required dependencies using pip and the provided requirements.txt file:

    ```
    pip install -r requirements.txt
    ```

### Setup

1. Create a virtual environment for the project:

    ```
    python -m venv venv
    ```

2. Activate the virtual environment:

    - On Windows:

        ```
        venv\Scripts\activate
        ```

    - On macOS and Linux:

        ```
        source venv/bin/activate
        ```

3. Create a `.env` file in the project root directory.

4. Add your Azure OpenAI API key and endpoint to the `.env` file:

    ```
    AZURE_OPENAI_API_KEY=your-api-key-here
    AZURE_OPENAI_ENDPOINT=your-openai-endpoint-here
    ```

### Running the App

Once you've installed the dependencies and set up your environment variables, you can run the app:

    python app.py


The app will start running locally, and you can access it in your web browser at `http://localhost:5000`.

## Contributing

If you'd like to contribute to the Military Transition Support App, please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License.
