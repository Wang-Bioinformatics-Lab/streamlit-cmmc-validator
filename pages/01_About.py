import streamlit as st

def about_page():
    st.title("About the USI, SMILES, and Metadata Validator")

    st.markdown("""
    ### Overview
    This project provides a tool for validating **Universal Spectrum Identifiers (USIs)**, **SMILES strings**, and various metadata fields with controlled vocabularies. It is designed to help ensure that the datasets follow the correct formatting for deposition data on [CMMC](https://cmmc.gnps2.org/).

    ### Key Features
    - **Header Validation**: Checks if the uploaded TSV file contains all the required headers.
    - **USI Validation**: Validates the format and existence of USIs using an external API.
    - **SMILES Validation**: Verifies SMILES strings via an API to ensure proper chemical structure formatting.
    - **Controlled Vocabulary Validation**: Ensures fields like `input_molecule_origin`, `input_confirmation`, and `input_source` match expected values.
    - **Case-Insensitive Validation**: Handles case-insensitive input for controlled vocabulary fields.

    ### Who is this for?
    This tool is intended for:
    - Anyone who needs to validate USIs, SMILES strings, or metadata for CMMC batch deposition.

    ### How to Use the Tool
    1. **Upload** a TSV file containing the data you want to validate.
    2. The tool will automatically:
        - Validate the headers.
        - Check the USIs using a remote API.
        - Validate the SMILES strings via an external API.
        - Ensure fields with controlled vocabulary match the valid options.
    3. Download the validated file for further inspection.
    4. Upload data through the [CMMC deposition workflow](https://gnps2.org/workflowinput?workflowname=cmmc_deposition_workflow).

    ### Learn More
    - **Source Code**: [GitHub Repository](https://github.com/Wang-Bioinformatics-Lab/streamlit-cmmc-validator)
    - **Documentation**: Check the full documentation in the repository for more details about setup, usage, and contributing.


    ### License
    This project is licensed under the GPL-3.0 license. Feel free to use, modify, and distribute the tool as needed.
    """)

# Call the about_page function to render the "About" page
about_page()
