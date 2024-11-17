// Protein API endpoint (replace with your Python backend API URL)
const proteinAPI = "http://localhost:5000/api/protein/"; // Replace with the actual URL

// Function to fetch protein data from the Python backend
async function fetchProteinData(uniprotAccession) {
    try {
        const response = await fetch(`${proteinAPI}${uniprotAccession}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching protein data:', error);
    }
}

// Function to update the model and display protein info
function updateModel(uniprotAccession) {
    fetchProteinData(uniprotAccession).then(data => {
        if (data) {
            // Update the description and protein name
            document.getElementById("description").innerText = data.description || "No description available.";
            document.getElementById("proteinName").innerText = data.name ? `Protein: ${data.name}` : "Protein name unavailable";

            // Load the model into the 3D viewer (using the model URL received from backend)
            loadModel(data.modelUrl);  // The model URL will be provided by the backend
        }
    });
}

// Function to load the model into the 3Dmol.js viewer
function loadModel(modelUrl) {
    const viewer = new $3Dmol.view("modelViewer", {
        width: 800,
        height: 600,
        backgroundColor: "white"
    });

    // Fetch and load the model data (e.g., CIF or PDB format)
    fetch(modelUrl)
        .then(response => response.text())
        .then(modelData => {
            viewer.addModel(modelData, 'cif');  // Adjust format based on your model type
            viewer.setStyle({}, { cartoon: { color: "spectrum" } });
            viewer.zoomTo();
            viewer.render();
        })
        .catch(error => {
            console.error('Error loading the model:', error);
        });
}

// Call updateModel with a specific UniProt accession (example UniProt accession)
const uniprotAccession = "A0A0C5B5G6";  // Example UniProt accession, replace with your desired accession
updateModel(uniprotAccession);
