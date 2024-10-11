# Data Validation Script for USI, SMILES, and Metadata

This repository contains a Python script and a cloud-hosted app (https://usi-smiles-validator.streamlit.app/) designed to validate USI (Universal Spectrum Identifier), SMILES strings, and several metadata fields (`input_molecule_origin`, `input_confirmation`, `input_source`). The validation process checks for valid entries and flags rows with incorrect or invalid data.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Cloud Application](#cloud-application)
- [Valid Entries](#valid-entries)
- [Troubleshooting](#troubleshooting)

## Features

- **Case-insensitive validation** for the following fields:
  - `input_molecule_origin`
  - `input_confirmation`
  - `input_source`
- **API validation** for SMILES strings and USIs.
- Outputs detailed error messages for invalid rows.
- **Cloud-hosted Streamlit app** for convenient use without local installation.

## Requirements

- Python 3.7 or higher
- The following Python libraries:
  - `pandas`
  - `requests`
  - `streamlit` (optional, if you want to run the Streamlit app locally)

## Installation

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/wilhan-nunes/usi-smiles-validator.git
    ```

2. Navigate to the project directory:

    ```bash
    cd usi-smiles-validator
    ```

3. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To validate the deposition dataset, prepare a TSV file with the following template (https://tinyurl.com/frku9zys).
The columns that will be validated are:

- `input_usi`
- `input_structure`
- `input_molecule_origin`
- `input_confirmation`
- `input_source`

### Example script usage:

This will run the app locally:
```bash
streamlit run app.py
```

## Cloud Application

You can also use the cloud-hosted Streamlit application to perform validation without needing to install anything locally.

**Access the app here**: [USI and SMILES Validator](https://usi-smiles-validator.streamlit.app/)

## Valid Entries

### input_molecule_origin
- Microbial metabolism of drugs
- Microbial metabolism of food molecules
- Microbial metabolism of other human-made molecules
- Microbial metabolism of host-derived molecules
- Microbial metabolism of microbial-derived molecules
- Host metabolism of microbial metabolites
- De novo biosynthesis by microbes (e.g., natural products and other specialized metabolites)
- Diet
- Unknown/Undefined

### input_confirmation
- confirmed
- predicted

### input_source
- Microbial
- Microbial and Host
- Microbial and Diet
- Microbial, Host, and Diet
- Diet
- Unknown

## Troubleshooting

If you encounter any issues, here are a few tips:

- **Case-sensitivity**: The script performs case-insensitive validation, but make sure to remove any unnecessary spaces in the TSV file.
- **SMILES validation errors**: If you receive errors during SMILES validation, ensure that your SMILES strings are formatted correctly AND are valid (use https://structure.gnps2.org/convert?smiles={your_smiles}).
- **USI validation**: Ensure that the USI strings follow the correct format. The script allows multiple USIs separated by semicolons. If the HTTP responde that caused the failing is 500, the USI is probably valid, but the server faced some internal issue. Please manually verify if this is the case accessing https://metabolomics-usi.gnps2.org/json/?usi1={your_500_code_usi}). If the page loads with a peak list, you are good to go. 

If problems persist, please open an issue in the GitHub repository.

