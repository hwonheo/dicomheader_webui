# DicomHeader::Web

A web-based tool for sorting and organizing DICOM files based on their SeriesDescription and SliceThickness.

## Features

- Automatically sorts DICOM files into structured folders
- User-friendly web interface
- Real-time progress updates
- Supports both Korean and English languages

## Installation

1. Clone the repository:

```bash
git clone https://github.com/hwonheo/dicomheader_webui.git
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

python app.py


2. Open a web browser and navigate to `http://localhost:5000`
3. Enter the root directory containing DICOM files
4. Optionally, specify an output directory
5. Click "Start Sorting" to begin the process


## Project Structure

```
dicomheader_webui/
├── README.md
├── requirements.txt
├── app.py
├── workflow_manager.py
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.