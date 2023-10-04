import requests

# Step 1: ESearch to get IDs
esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
params = {
    "db": "nucleotide",
    "term": "Homo Sapiens[Orgn]",
    "retmode": "json",
    "retmax": 100
}
response = requests.get(esearch_url, params=params)
ids = ",".join(response.json()['esearchresult']['idlist'])

# Step 2: EFetch to get FASTA data
efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
params = {
    "db": "nucleotide",
    "id": ids,
    "rettype": "fasta",
    "retmode": "text"
}
response = requests.get(efetch_url, params=params)

# Output the FASTA data
print(response.text)


with open("output.fasta", "w") as outfile:
    outfile.write(response.text)