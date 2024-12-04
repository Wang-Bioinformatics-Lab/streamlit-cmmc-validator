import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import requests
import time
import re
import urllib.parse


# Function to check SMILES using the API
def check_smiles(smiles):
    encoded_smiles = urllib.parse.quote(smiles, safe='')
    url = f"https://structure.gnps2.org/convert?smiles={encoded_smiles}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return "Ok"
        else:
            return f"FAILED {response.status_code}"
    except Exception as e:
        return f"Error {e}"


# Test function for validating a USI
def is_valid_usi(usi):
    # USI pattern allowing '/ ', '- ', and spaces
    usi_pattern = r'^mzspec:[A-Za-z0-9\-_/\. ]+:[A-Za-z0-9\-_/\. ]+:[A-Za-z0-9\-_/\. ]+(:[A-Za-z0-9\-_/\. ]*)?$'
    return bool(re.match(usi_pattern, usi))

# Function to check USI(s) using the API with retries
def usi_request(usi: str, max_attempts=3):
    # Handle cases where multiple USIs are separated by ';'
    usis = usi.split(';')
    results = {}

    for u in usis:
        if is_valid_usi(u.strip()):
            attempts = 0
            result = "FAILED"
            while attempts < max_attempts:  # Try up to max_attempts times
                print(f'Requesting {u} (Attempt {attempts + 1})')

                try:
                    response = requests.get(f'https://metabolomics-usi.gnps2.org/json/?usi1={u.strip()}')

                    if response.status_code == 200:
                        print(f'Attempt {attempts + 1} successful for {u}.')
                        result = 'Ok'
                        break
                    else:
                        print(f'Attempt {attempts + 1} failed for {u}.')
                        print(f'Status code: {response.status_code}.')

                except requests.RequestException as e:
                    print(f'Error during request for {u}: {e}')
                    result = f"Error {e}"
                    break

                # Increment attempts and sleep before retrying
                attempts += 1
                time.sleep(1)

            if attempts == max_attempts and result != "Ok":
                print(f'{u} failed after {max_attempts} attempts. Please verify if it is valid.')
                result = f"FAILED - Status code {response.status_code}"
            # Store the result for each USI
            results[u] = result
        else:
            print(f'{u} failed because it is an invalid USI.')
            results[u] = 'FAILED - Invalid USI'

    # Return the result dictionary with status for each USI
    return results

def retrieve_validation_lists(tsv_file):
    df = pd.read_csv(tsv_file, sep='\t')

    valid_headers = list(df.columns)
    valid_confirmation = df[
        'input_confirmation'].dropna().str.upper().tolist() if 'input_confirmation' in df.columns else []
    valid_molecule_origin = df[
        'input_molecule_origin'].dropna().str.upper().tolist() if 'input_molecule_origin' in df.columns else []
    valid_source = df['input_source'].dropna().str.upper().tolist() if 'input_source' in df.columns else []

    return {
        'valid_headers': valid_headers,
        'valid_confirmation': valid_confirmation,
        'valid_molecule_origin': valid_molecule_origin,
        'valid_source': valid_source
    }


def validate_molecule_origin(entry, valid_list):
    if pd.isnull(entry):
        return "FAILED. No Data provided. Mandatory field."

    # Split entries by semicolon and strip whitespace
    origins = [origin.strip().upper() for origin in str(entry).split(';')]

    # Check if ALL entries are in the valid list
    invalid_origins = [origin for origin in origins if origin not in valid_list]

    if not invalid_origins:
        return "Ok"
    else:
        return f"FAILED: Invalid origin(s) - {', '.join(invalid_origins)}"

# Function to validate entries based on valid lists
def validate_entry(entry, valid_list):
    if pd.isnull(entry):
        return "FAILED. No Data provided. Mandatory field."
    elif entry.strip().upper() in valid_list:
        return "Ok"
    else:
        return "FAILED"

# Download and load validation data from reference file
validation_data_file = './controlled_vocabulary.tsv'
validation_data = retrieve_validation_lists(validation_data_file)

# Function to validate headers
def validate_headers(uploaded_headers, expected_headers):
    missing_headers = [header for header in expected_headers if header not in uploaded_headers]
    if missing_headers:
        return False, missing_headers
    return True, None

# Streamlit UI
# Add a tracking token
html('<script async defer data-website-id="1a70457c-e452-4e8f-822b-9983d742e174" src="https://analytics.gnps2.org/umami.js"></script>', width=0, height=0)

st.title("CMMC Validator")
st.markdown("""
The validation process will check if:

1. **All the headers** are present and valid.
2. **USI's** are correctly formatted and validated.
3. **SMILES strings** are properly formatted and validated.
4. Fields with **controlled vocabulary** are checked for validity.
""")

st.markdown("[Link to deposition file template](https://docs.google.com/spreadsheets/d/1ZF7uW3PxmOMMEJkiwDkHceI-W5aw2NE4aDc37kYDhNw/edit?usp=sharing)")

# File upload
uploaded_file = st.file_uploader("Choose a TSV file", type="tsv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep='\t')

    # Validate headers
    st.write("Validating file headers...")
    uploaded_headers = list(df.columns)
    expected_headers = validation_data['valid_headers']

    headers_valid, missing_headers = validate_headers(uploaded_headers, expected_headers)

    if headers_valid:
        st.success("Headers are valid.", icon='✅')

        # Validate USI
        with st.spinner('Validating USIs...'):
            df['usi_validation_details'] = df['input_usi'].apply(lambda x: usi_request(x) if pd.notnull(x) else {"No USI": "Ok"})

        # Validate SMILES
        with st.spinner('Validating SMILES...'):
            df['smiles_validation'] = df['input_structure'].apply(
                lambda x: check_smiles(x) if pd.notnull(x) else "No SMILES")

        # Validate input_molecule_origin
        with st.spinner('Validating input_molecule_origin...'):
            df['molecule_origin_validation'] = df['input_molecule_origin'].apply(
                lambda x: validate_molecule_origin(x, validation_data['valid_molecule_origin']))

        # Validate input_confirmation
        with st.spinner('Validating input_confirmation...'):
            df['confirmation_validation'] = df['input_confirmation'].apply(lambda x: validate_entry(x, validation_data['valid_confirmation']))

        # Validate input_source
        with st.spinner('Validating input_source...'):
            df['source_validation'] = df['input_source'].apply(lambda x: validate_entry(x, validation_data['valid_source']))

        # Show updated DataFrame
        st.write("Validated Data:")
        st.dataframe(df.head())

        # Show rows with failed validations
        failed_usi = df[df['usi_validation_details'].apply(
            lambda x: any(v.startswith("FAILED") or v.startswith("Error") for v in x.values()))]
        failed_smiles = df[df['smiles_validation'].str.startswith('FAILED')]
        failed_molecule_origin = df[df['molecule_origin_validation'].str.startswith('FAILED')]
        failed_confirmation = df[df['confirmation_validation'].str.startswith('FAILED')]
        failed_source = df[df['source_validation'].str.startswith('FAILED')]

        st.write(f"Failed USIs: {len(failed_usi)}")
        st.dataframe(failed_usi[['input_usi', 'usi_validation_details']])

        st.write(f"Failed SMILES: {len(failed_smiles)}")
        st.dataframe(failed_smiles[['input_structure', 'smiles_validation']])

        st.write(f"Failed input_molecule_origin: {len(failed_molecule_origin)}")
        st.dataframe(failed_molecule_origin[['input_molecule_origin', 'molecule_origin_validation']])

        st.write(f"Failed input_confirmation: {len(failed_confirmation)}")
        st.dataframe(failed_confirmation[['input_confirmation', 'confirmation_validation']])

        st.write(f"Failed input_source: {len(failed_source)}")
        st.dataframe(failed_source[['input_source', 'source_validation']])

        # Allow downloading the updated file with validation status
        output_filename = "validated_usis_smiles_metadata.tsv"
        df.to_csv(output_filename, sep='\t', index=False)

        with open(output_filename, "rb") as file:
            st.download_button(
                label="Download the validated file",
                data=file,
                file_name=output_filename,
                mime="text/tab-separated-values"
            )
    else:
        st.error(
            f"Missing headers: {', '.join(missing_headers)}. Please upload a file with all required headers.", icon='🚨')
        st.warning('Tip: if you think all headers are present, check for spelling errors. See the template link on the top of the page.', icon='💡')
