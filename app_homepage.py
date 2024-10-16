import streamlit as st
import pandas as pd
import requests
import time


# Function to check SMILES using the API
def check_smiles(smiles):
    url = f"https://structure.gnps2.org/convert?smiles={smiles}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return "Ok"
        else:
            return "FAILED"
    except Exception as e:
        return f"Error {e}"


# Function to check USI(s) using the API with retries
def usi_request(usi: str, max_attempts=3):
    # Handle cases where multiple USIs are separated by ';'
    usis = usi.split(';')
    results = {}

    for u in usis:
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

    # Return the result dictionary with status for each USI
    return results

def retrieve_validation_lists(url, file_path='validation_tsv.tsv'):
    response = requests.get(url)
    response.raise_for_status()

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response.text)

    df = pd.read_csv(file_path, sep='\t')

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

# Function to validate entries based on valid lists
def validate_entry(entry, valid_list):
    if pd.isnull(entry):
        return "No Data. Mandatory field."
    elif entry.strip().upper() in valid_list:
        return "Ok"
    else:
        return "FAILED"

# Download and load validation data from google sheet reference file
url = 'https://docs.google.com/spreadsheets/d/1ZF7uW3PxmOMMEJkiwDkHceI-W5aw2NE4aDc37kYDhNw/export?format=tsv&gid=724969182'
validation_data = retrieve_validation_lists(url)

# Function to validate headers
def validate_headers(uploaded_headers, expected_headers):
    missing_headers = [header for header in expected_headers if header not in uploaded_headers]
    if missing_headers:
        return False, missing_headers
    return True, None

# Streamlit UI
st.title("USI, SMILES, and Metadata Validator for CMMC batch deposition")
# st.write("Upload a TSV file to validate the USI, SMILES, and metadata columns. It will check if: 1. All the headers are there and are valid; 2. Validate USI's; 3. Validate Smiles; 4. Validate fileds with controlled vocabulary.")
st.markdown("""
### Upload a TSV file to validate the USI, SMILES, and metadata columns.

The validation process will check if:

1. **All the headers** are present and valid.
2. **USI's** are correctly formatted and validated.
3. **SMILES strings** are properly formatted and validated.
4. Fields with **controlled vocabulary** are checked for validity.
""")

st.write("Template:  https://tinyurl.com/frku9zys")

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
        st.write("Validating USIs...")
        df['usi_validation_details'] = df['input_usi'].apply(lambda x: usi_request(x) if pd.notnull(x) else "No USI")

        # Validate SMILES
        st.write("Validating SMILES...")
        df['smiles_validation'] = df['input_structure'].apply(
            lambda x: check_smiles(x) if pd.notnull(x) else "No SMILES")

        # Validate input_molecule_origin
        st.write("Validating input_molecule_origin...")
        df['molecule_origin_validation'] = df['input_molecule_origin'].apply(
            lambda x: validate_entry(x, validation_data['valid_molecule_origin']))

        # Validate input_confirmation
        st.write("Validating input_confirmation...")
        df['confirmation_validation'] = df['input_confirmation'].apply(lambda x: validate_entry(x, validation_data['valid_confirmation']))

        # Validate input_source
        st.write("Validating input_source...")
        df['source_validation'] = df['input_source'].apply(lambda x: validate_entry(x, validation_data['valid_source']))

        # Show updated DataFrame
        st.write("Validated Data:")
        st.dataframe(df.head())

        # Show rows with failed validations
        failed_usi = df[df['usi_validation_details'].apply(
            lambda x: any(v == "FAILED" or v.startswith("Error") for v in x.values()))]
        failed_smiles = df[df['smiles_validation'] == 'FAILED']
        failed_molecule_origin = df[df['molecule_origin_validation'] == 'FAILED']
        failed_confirmation = df[df['confirmation_validation'] == 'FAILED']
        failed_source = df[df['source_validation'] == 'FAILED']

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