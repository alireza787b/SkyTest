
# SkyTest - Dynamic Data Collection Platform

SkyTest is an innovative, web-based platform designed to facilitate the dynamic documentation and analysis of test logs across various projects. It stands out by allowing users to customize data collection forms via a simple JSON configuration, making it versatile for a wide range of projects.

## Key Features

- **Bootstrap Full Responsiveness**: Ensures that the application is mobile-friendly and provides a seamless user experience across various devices and screen sizes.
- **Import/Export Functionality**: Offers capabilities to import and export test data along with attachments and form definitions, allowing for easy data backup and restoration.
- **Multiple File Upload**: Enhances data entry by allowing multiple files to be uploaded as part of test documentation, supporting images, videos, and log files. It is crucial to maintain the "attachments" field name in the tests structure JSON for the application to function correctly.

## Getting Started

Follow these instructions to set up SkyTest in your local environment.

### Prerequisites

- Python 3
- Flask

Ensure Python and Flask are installed on your system. SkyTest utilizes Flask, a lightweight WSGI web application framework, to serve web content.

### Environment Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/alireza787b/SkyTest.git
    cd SkyTest
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Initialize the database**:
    *Note: This step is only required the first time you set up the project or whenever you make changes to the JSON configuration for the form fields.*
    ```bash
    python initialize_db.py
    ```

5. **Run the application**:
    ```bash
    python run.py
    ```
    The application will be available at `http://localhost:5562` (or whatever port defined in the `config.py`).

## Configuration

SkyTest's form fields and structures are defined in JSON files within the `definitions` folder. It is essential to maintain the "attachments" field name in the tests structure JSON for the application to operate normally.
Other settings can be customized through the `config.py`.


## Contributing

SkyTest is open to contributions. Whether it's adding new features, enhancing existing ones, or improving the UI/UX, your contributions are welcome.

## License

SkyTest is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for more details.
