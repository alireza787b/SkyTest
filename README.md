# SkyTest - Dynamic Data Collection Platform

SkyTest is an innovative, web-based platform designed to facilitate the dynamic documentation and analysis of test logs across various projects. Originating with a focus on documenting flight test data for drones and aerial vehicles, its adaptable framework makes it equally applicable to diverse fields requiring detailed test documentation. SkyTest stands out by allowing users to customize data collection forms via a simple JSON configuration, making it a versatile tool for projects ranging from aviation to software development and beyond.

## Key Features

- **Dynamic Form Creation**: Automatically generates forms based on a JSON configuration file, enabling quick adaptation to changing data collection requirements without direct code alterations.
- **Efficient Data Management**: Built on Flask and Flask-SQLAlchemy, offering a solid foundation for performing Create, Read, Update, and Delete (CRUD) operations on test entries.
- **Versatile Field Support**: Supports a wide array of field types including text inputs, numbers, selections, and date pickers, catering to a broad spectrum of data collection needs.
- **Automated Field Population**: Facilitates automatic assignment of certain values such as unique test identifiers and current dates, streamlining the data entry process.
- **Comprehensive Data Viewing**: Provides a detailed interface for reviewing submitted data, with capabilities to display extensive test details and handle empty fields gracefully.

## Getting Started

Follow these instructions to set up SkyTest in your local environment.

### Prerequisites

- Python 3
- Flask

Ensure Python and Flask are installed on your system. SkyTest utilizes Flask, a lightweight WSGI web application framework, to serve web content.

### Setup

1. **Clone the repository**:

```bash
git clone https://github.com/alireza787b/SkyTest.git
cd SkyTest
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Initialize the database**:

*Note: This step is only required the first time you set up the project or whenever you make changes to the JSON configuration for the form fields.*

```bash
python initialize_db.py
```

4. **Run the application**:

```bash
python run.py
```

The application will be available at `http://localhost:5000/`.

## Configuration

SkyTest's form fields are defined in a JSON configuration file, making it straightforward to modify or extend the data collection forms to meet your specific requirements.

## Contributing

SkyTest is actively evolving, with enhancements to the user interface and additional features in the pipeline. Contributions are welcome! Feel free to fork the project, make improvements, and submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
