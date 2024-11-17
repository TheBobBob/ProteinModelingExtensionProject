import requests
import gzip
from io import BytesIO

API = "https://rest.uniprot.org/uniprotkb/stream?compressed=true&fields=accession%2Cid&format=tsv&query=(reviewed:true)%20AND%20(annotation_score:5)"
#maybe also only get the ones that have 5/5 annotation score
response = requests.get(API)

if response.headers.get('Content-Encoding') == 'gzip':
    buf = BytesIO(response.content)
    with gzip.GzipFile(fileobj=buf) as f:
        decompressed_data = f.read().decode('utf-8')
    with open("IDS.txt", "w", encoding = "utf-8") as file:
        file.write(decompressed_data)
else:
    # If the response is not compressed, print it directly
    with open("IDS.txt", "w", encoding = "utf-8") as file:
        file.write(response.text)
