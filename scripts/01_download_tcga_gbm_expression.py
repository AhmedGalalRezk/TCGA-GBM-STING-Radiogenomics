from pathlib import Path
import json
import requests
import pandas as pd
from tqdm import tqdm

PROJECT_ROOT = Path.home() / "Desktop" / "TCGA_GBM_Radiogenomics"
RAW_DIR = PROJECT_ROOT / "data" / "gdc_raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

FILES_ENDPOINT = "https://api.gdc.cancer.gov/files"
DATA_ENDPOINT = "https://api.gdc.cancer.gov/data"

filters = {
    "op": "and",
    "content": [
        {
            "op": "in",
            "content": {
                "field": "cases.project.project_id",
                "value": ["TCGA-GBM"]
            }
        },
        {
            "op": "in",
            "content": {
                "field": "files.data_category",
                "value": ["Transcriptome Profiling"]
            }
        },
        {
            "op": "in",
            "content": {
                "field": "files.data_type",
                "value": ["Gene Expression Quantification"]
            }
        },
        {
            "op": "in",
            "content": {
                "field": "files.analysis.workflow_type",
                "value": ["STAR - Counts"]
            }
        },
        {
            "op": "in",
            "content": {
                "field": "files.access",
                "value": ["open"]
            }
        },
        {
            "op": "in",
            "content": {
                "field": "cases.samples.sample_type",
                "value": ["Primary Tumor"]
            }
        }
    ]
}

fields = [
    "file_id",
    "file_name",
    "file_size",
    "cases.submitter_id",
    "cases.samples.submitter_id",
    "cases.samples.sample_type"
]

params = {
    "filters": json.dumps(filters),
    "fields": ",".join(fields),
    "format": "JSON",
    "size": "1000"
}

response = requests.get(
    FILES_ENDPOINT,
    params=params,
    timeout=120
)
response.raise_for_status()

hits = response.json()["data"]["hits"]

print(f"Files found: {len(hits)}")

records = []

for hit in hits:
    cases = hit.get("cases", [])

    if not cases:
        continue

    patient_id = cases[0].get("submitter_id")

    samples = cases[0].get("samples", [])
    sample_id = samples[0].get("submitter_id") if samples else None
    sample_type = samples[0].get("sample_type") if samples else None

    records.append({
        "file_id": hit["file_id"],
        "file_name": hit["file_name"],
        "file_size": hit.get("file_size"),
        "patient_id": patient_id,
        "sample_id": sample_id,
        "sample_type": sample_type
    })

manifest = pd.DataFrame(records)

manifest = manifest.dropna(
    subset=["file_id", "patient_id", "sample_id"]
)

manifest = manifest.sort_values(
    ["patient_id", "sample_id"]
)

manifest.to_csv(
    PROCESSED_DIR / "TCGA_GBM_expression_manifest.csv",
    index=False
)

print(f"Unique patients: {manifest['patient_id'].nunique()}")
print(f"Unique samples: {manifest['sample_id'].nunique()}")
print(manifest.head())

for row in tqdm(
    manifest.itertuples(index=False),
    total=len(manifest),
    desc="Downloading STAR-count files"
):
    patient_dir = RAW_DIR / row.patient_id
    patient_dir.mkdir(parents=True, exist_ok=True)

    output_file = patient_dir / row.file_name

    if output_file.exists() and output_file.stat().st_size > 0:
        continue

    url = f"{DATA_ENDPOINT}/{row.file_id}"

    with requests.get(url, stream=True, timeout=300) as download:
        download.raise_for_status()

        with open(output_file, "wb") as handle:
            for chunk in download.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)


print("Download complete.")







