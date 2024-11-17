import requests
import json
import py3Dmol
from IPython.display import display

# Function to retrieve protein information from AlphaFold API
def get_protein(uniprot_accession):
    api_endpoint = "https://alphafold.ebi.ac.uk/api/prediction/"
    url = f"{api_endpoint}{uniprot_accession}"  # Construct the URL for API

    try:
        # Use a timeout to handle potential connection issues
        response = requests.get(url, timeout=10)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Function to retrieve protein summary from UniProt API
def get_protein_function(uniprot_accession, eco_filter=None):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_accession}.txt"
    response = requests.get(url)
    
    if response.status_code == 200:
        lines = response.text.splitlines()
        
        function_lines = []
        is_function_section = False
        for line in lines:
            # Start of the function section
            if line.startswith("CC   -!- FUNCTION:"):
                is_function_section = True
            
            # Collect function description lines
            if is_function_section:
                function_lines.append(line[5:].strip())  # Skip the 'CC   -!- ' part
                
                # Stop collecting when reaching CATALYTIC ACTIVITY or ECO code
                if "CC   -!- CATALYTIC ACTIVITY:" in line or " {ECO:" in line:
                    break
        
        # If ECO filter is provided, filter the function description based on the ECO code
        if eco_filter:
            function_lines = [line for line in function_lines if any(eco in line for eco in eco_filter)]
        
        # Join all the lines that are part of the function description
        function_summary = " ".join(function_lines)
        return function_summary if function_summary else "No function description found."
    
    else:
        return f"Error: Unable to retrieve data for {uniprot_accession}, status code {response.status_code}"

# Function to display protein structure and function
def show_structure_and_image(model_url, color="lDDT"):
    try:
        # Retrieve the model data from the URL
        model_data = requests.get(model_url).text

        # Create a 3Dmol.js view
        view = py3Dmol.view(js='https://3dmol.org/build/3Dmol.js',)

        # Add the model data to the view
        view.addModel(model_data, 'cif')  # Assuming the format is 'cif' based on the URL

        # Set style based on color parameter
        if color == "lDDT":
            view.setStyle({'cartoon': {'colorscheme': {'prop': 'b', 'gradient': 'roygb', 'min': 50, 'max': 90}}})
        elif color == "rainbow":
            view.setStyle({'cartoon': {'color': 'spectrum'}})

        # Zoom to the structure
        view.zoomTo()

        # Display the 3D structure
        display(view)
    except Exception as e:
        print(f"Error displaying structure: {e}")

# Main function to visualize protein from UniProt accession
def visualize_protein(uniprot_accession, color="lDDT"):
    protein_info = get_protein(uniprot_accession)

    if protein_info:
        # Ensure protein_info is a list and properly structured
        if isinstance(protein_info, list) and len(protein_info) > 0:
            protein = protein_info[0]  # First entry in the list

            # Print the JSON formatted protein information
            print(json.dumps(protein_info, indent=2))

            # Extract the UniProt accession and model-related URLs
            name_of_protein = protein.get('uniprotDescription', 'Unknown')
            model_url = protein.get('cifUrl')  # Changed to cifUrl based on your data

            if model_url:
                # Show the protein structure
                show_structure_and_image(model_url, color)

                # Fetch and display protein summary
                protein_summary = get_protein_function(uniprot_accession)
                if protein_summary:
                    print(f"Protein Summary: {protein_summary}")
                    print(f"Name of Protein: {name_of_protein}")
                else:
                    print("No summary available.")
            else:
                print("Failed to retrieve model URL.")
        else:
            print("Error: Unexpected response format from requests.")
    else:
        print("Failed to retrieve protein information.")

# Example: Replace 'A0A0C5B5G6' with the desired UniProt accession
uniprot_accession = "A0A1M4NG14"  # Example UniProt accession
visualize_protein(uniprot_accession)
