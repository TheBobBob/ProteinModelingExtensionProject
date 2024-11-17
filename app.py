from flask import Flask, jsonify, render_template, request
import requests
import py3Dmol
from IPython.display import display
import json

app = Flask(__name__)

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

# Function to serve the protein structure and data to the frontend
@app.route("/api/protein/<uniprot_accession>")
def protein_info(uniprot_accession):
    protein_info = get_protein(uniprot_accession)

    if protein_info:
        if isinstance(protein_info, list) and len(protein_info) > 0:
            protein = protein_info[0]
            model_url = protein.get('cifUrl')  # Changed to cifUrl based on your data

            #so basically the way that the protein has to be visualized is not sent to the index.html and that is why it is not working 
            
            if model_url:
                # Retrieve protein function summary
                protein_summary = get_protein_function(uniprot_accession)
                # Prepare data to send to the frontend
                response_data = {
                    "uniprot_accession": uniprot_accession,
                    "protein_name": protein.get('uniprotDescription', 'Unknown'),
                    "protein_summary": protein_summary,
                    "model_url": model_url
                }
                return jsonify(response_data)
            else:
                return jsonify({"error": "Failed to retrieve model URL."}), 404
        else:
            return jsonify({"error": "Unexpected response format from AlphaFold API."}), 400
    else:
        return jsonify({"error": "Failed to retrieve protein information."}), 404

# Frontend page to display protein and structure
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
