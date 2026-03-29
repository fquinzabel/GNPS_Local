#!/usr/bin/env python3
"""
getGNPS_library_annotations_local.py

Local replacement for getGNPS_library_annotations.py.

The original script enriched library search hits by calling the GNPS API
(gnps.ucsd.edu) for each CCMSLIB spectrum ID. With GNPS shut down, those
calls time out. This script instead maps the binary's raw output column
names directly to the column names expected by downstream scripts.

Binary output column names (main_execmodule.allcandidates) vs expected:
  #Scan#              -> #Scan#          (direct)
  MQScore             -> MQScore         (direct, also = MatchingScore)
  CompoundName        -> Compound_Name
  LibrarySpectrumID   -> SpectrumID
  Smiles              -> Smiles + SMILES
  Inchi               -> INCHI + InChI
  mzErrorPPM          -> MZErrorPPM
  LibSearchSharedPeaks-> SharedPeaks
  ParentMassDiff      -> MassDiff
  Organism            -> Compound_Source
  LibraryName         -> LibraryName     (direct)
  SpectrumFile        -> SpectrumFile    (direct)
  SpecMZ              -> Precursor_MZ
  ExactMass           -> ExactMass       (direct)
  Charge              -> (not in output schema)
  Adduct is embedded in Annotation field as "CompoundName M+H" format

Columns not produced by the binary (Instrument, Ion_Source, PI,
Data_Collector, tags, Library_Class, IonMode, Adduct, FormulaString,
InChIKey, TotalPeaks, NumPeaks, MirrorLibraryName, Title, Retention_Time)
are filled with "N_A".

Same CLI interface as the original:
    python getGNPS_library_annotations_local.py <input.tsv> <output.tsv> --topk 1
"""

import argparse
import csv
import sys
from collections import defaultdict

# Output column set expected by downstream scripts:
#   enrich_clusterinfosummary.py  reads: #Scan#, MQScore, Smiles, INCHI,
#                                        Compound_Name, SpectrumID
#   molecular_network_filtering_library.py reads: #Scan#, Compound_Name,
#       Adduct, INCHI, Smiles, MQScore, MassDiff, MZErrorPPM, SharedPeaks,
#       tags, Library_Class, Instrument, IonMode, Ion_Source, PI,
#       Data_Collector, Compound_Source, SpectrumID
OUTPUT_FIELDNAMES = [
    "#Scan#", "SpectrumFile", "LibraryName", "MirrorLibraryName", "SpectrumID",
    "Title", "Compound_Name", "Retention_Time", "MZErrorPPM", "SMILES", "InChI",
    "InChIKey", "FormulaString", "IonMode", "Adduct", "ExactMass", "Precursor_MZ",
    "SharedPeaks", "TotalPeaks", "MatchingScore", "NumPeaks",
    "MQScore", "Smiles", "INCHI",
    "MassDiff", "tags", "Library_Class", "Instrument", "Ion_Source",
    "PI", "Data_Collector", "Compound_Source",
]

# Pandas silently converts these strings to float NaN even with dtype=str.
# Use "N_A" (underscore) as the safe sentinel — it is not on this list.
_PANDAS_NA = {
    "", "n/a", "na", "nan", "none", "null",
    "#n/a", "#na", "#n/a n/a", "<na>",
    "-nan", "-1.#ind", "-1.#qnan", "1.#ind", "1.#qnan",
}


def s(v):
    """Sanitise a value to a non-NaN string safe for pandas dtype=str reads."""
    if v is None:
        return "N_A"
    sv = str(v).strip()
    return "N_A" if sv.lower() in _PANDAS_NA else sv


def map_row(hit):
    """
    Map a raw binary output row to the OUTPUT_FIELDNAMES schema.
    Binary column -> output column(s).
    """
    # Score: binary writes MQScore directly
    mq = s(hit.get("MQScore", ""))

    # Compound name: binary writes CompoundName (no underscore)
    compound_name = s(hit.get("CompoundName", ""))

    # SpectrumID: binary writes LibrarySpectrumID
    spectrum_id = s(hit.get("LibrarySpectrumID", ""))

    # SMILES: binary writes Smiles
    smiles = s(hit.get("Smiles", ""))

    # InChI: binary writes Inchi (lowercase i)
    inchi = s(hit.get("Inchi", ""))

    # MZ error: binary writes mzErrorPPM (lowercase m)
    mz_error = s(hit.get("mzErrorPPM", ""))

    # Shared peaks: binary writes LibSearchSharedPeaks
    shared_peaks = s(hit.get("LibSearchSharedPeaks", ""))

    # Mass diff: binary writes ParentMassDiff
    mass_diff = s(hit.get("ParentMassDiff", ""))

    # Compound source: binary writes Organism
    compound_source = s(hit.get("Organism", ""))

    # Adduct: binary embeds it in Annotation as "CompoundName M+H"
    # Extract the part after the last space-separated token that looks like an adduct
    adduct = "N_A"
    annotation = hit.get("Annotation", "")
    if annotation and annotation != "*..*":
        parts = annotation.strip().split(" ")
        if len(parts) >= 2:
            candidate = parts[-1]
            # Simple heuristic: adducts contain + or - and brackets or M
            if any(c in candidate for c in ("+", "-", "M", "[", "]")):
                adduct = s(candidate)

    return {
        "#Scan#":           s(hit.get("#Scan#", "")),
        "SpectrumFile":     s(hit.get("SpectrumFile", "")),
        "LibraryName":      s(hit.get("LibraryName", "")),
        "MirrorLibraryName":"N_A",
        "SpectrumID":       spectrum_id,
        "Title":            "N_A",
        "Compound_Name":    compound_name,
        "Retention_Time":   "N_A",
        "MZErrorPPM":       mz_error,
        "SMILES":           smiles,
        "InChI":            inchi,
        "InChIKey":         "N_A",
        "FormulaString":    "N_A",
        "IonMode":          "N_A",
        "Adduct":           adduct,
        "ExactMass":        s(hit.get("ExactMass", "")),
        "Precursor_MZ":     s(hit.get("SpecMZ", "")),
        "SharedPeaks":      shared_peaks,
        "TotalPeaks":       "N_A",
        "MatchingScore":    mq,
        "NumPeaks":         "N_A",
        "MQScore":          mq,
        "Smiles":           smiles,
        "INCHI":            inchi,
        "MassDiff":         mass_diff,
        "tags":             "N_A",
        "Library_Class":    "N_A",
        "Instrument":       "N_A",
        "Ion_Source":       "N_A",
        "PI":               "N_A",
        "Data_Collector":   "N_A",
        "Compound_Source":  compound_source,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_results",  help="librarysearch_results.tsv from merge step")
    parser.add_argument("output_results", help="librarysearch_results_db.tsv output path")
    parser.add_argument("--topk", type=int, default=1,
                        help="Keep top-K hits per query scan (default: 1)")
    args = parser.parse_args()

    # ── Read input ────────────────────────────────────────────────────────────
    try:
        with open(args.input_results, "r", errors="replace") as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = list(reader)
    except Exception as e:
        print(f"ERROR reading {args.input_results}: {e}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("No hits in input — writing header-only output", file=sys.stderr)
        with open(args.output_results, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES,
                           delimiter="\t").writeheader()
        return

    print(f"Processing {len(rows)} hits, keeping top {args.topk} per scan",
          file=sys.stderr)

    # Detect scan column defensively
    first = rows[0]
    scan_col = next(
        (c for c in ("#Scan#", "Scan#", "scan", "#scan#") if c in first),
        list(first.keys())[0]
    )
    if scan_col != "#Scan#":
        print(f"WARNING: scan column is '{scan_col}', expected '#Scan#'",
              file=sys.stderr)

    # ── Group by scan, sort by MQScore descending, take top-K ────────────────
    by_scan = defaultdict(list)
    for row in rows:
        scan = row.get(scan_col, "")
        try:
            score = float(row.get("MQScore") or 0)
        except ValueError:
            score = 0.0
        by_scan[scan].append((score, row))

    output_rows = []
    for scan in sorted(by_scan.keys(), key=lambda x: int(x) if x.isdigit() else x):
        scored = sorted(by_scan[scan], key=lambda x: x[0], reverse=True)
        for _, hit in scored[:args.topk]:
            out = map_row(hit)
            # Override scan col normalisation if needed
            if scan_col != "#Scan#":
                out["#Scan#"] = s(hit.get(scan_col, ""))
            # Print SpectrumID to stdout (matches original script behaviour)
            print(out["SpectrumID"])
            output_rows.append(out)

    # ── Write output ──────────────────────────────────────────────────────────
    with open(args.output_results, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=OUTPUT_FIELDNAMES, delimiter="\t", extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote {len(output_rows)} rows to {args.output_results}", file=sys.stderr)


if __name__ == "__main__":
    main()