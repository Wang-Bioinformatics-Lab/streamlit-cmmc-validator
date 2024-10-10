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

# Validation for input_molecule_origin, input_confirmation, and input_source
valid_molecule_origin = [
    'MICROBIAL METABOLISM OF DRUGS',
    'MICROBIAL METABOLISM OF FOOD MOLECULES',
    'MICROBIAL METABOLISM OF OTHER HUMAN-MADE MOLECULES',
    'MICROBIAL METABOLISM OF HOST-DERIVED MOLECULES',
    'MICROBIAL METABOLISM OF MICROBIAL-DERIVED MOLECULES',
    'HOST METABOLISM OF MICROBIAL METABOLITES',
    'DE NOVO BIOSYNTHESIS BY MICROBES (E.G., NATURAL PRODUCTS AND OTHER SPECIALIZED METABOLITES)',
    'DIET',
    'UNKNOWN/UNDEFINED'
]

valid_confirmation = ["CONFIRMED", "PREDICTED"]

valid_source = [
    'MICROBIAL',
    'MICROBIAL AND HOST',
    'MICROBIAL AND DIET',
    'MICROBIAL, HOST, AND DIET',
    'DIET',
    'UNKNOWN'
]

# Function to validate entries based on valid lists
def validate_entry(entry, valid_list):
    if pd.isnull(entry):
        return "No Data"
    elif entry.strip() in valid_list:
        return "Ok"
    else:
        return "FAILED"

# Streamlit UI
st.title("USI, SMILES, and Metadata Validator")
st.write("Upload a TSV file to validate the USI, SMILES, and metadata columns.")
st.write("Template:  https://tinyurl.com/frku9zys")

# File upload
uploaded_file = st.file_uploader("Choose a TSV file", type="tsv")

if uploaded_file is not None:
    # Load the file into a DataFrame
    df = pd.read_csv(uploaded_file, sep='\t')

    st.write("Original Data:")
    st.dataframe(df.head())

    # Check if required columns are present
    if all(col in df.columns for col in
           ['input_usi', 'input_structure', 'input_molecule_origin', 'input_confirmation', 'input_source']):
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
            lambda x: validate_entry(x, valid_molecule_origin))

        # Validate input_confirmation
        st.write("Validating input_confirmation...")
        df['confirmation_validation'] = df['input_confirmation'].apply(lambda x: validate_entry(x, valid_confirmation))

        # Validate input_source
        st.write("Validating input_source...")
        df['source_validation'] = df['input_source'].apply(lambda x: validate_entry(x, valid_source))

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
        st.markdown("<p style='color:red;'>Error: The uploaded file must contain 'input_usi', 'input_structure', 'input_molecule_origin', 'input_confirmation', and 'input_source' columns.</p>", unsafe_allow_html=True)