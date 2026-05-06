# GNPS Local

Local optimization of GNPS Feature-Based Molecular Networking for single-user, 
offline metabolomics analysis on Windows 11 + WSL2.

## Original Work
This project is a derivative of [GNPS](https://gnps.ucsd.edu) ([GNPS_Workflows](https://github.com/CCMS-UCSD/GNPS_Workflows)) developed by the Dorrestein Lab at UC San Diego.

# User Guide

**Offline metabolomics molecular networking on your own computer**

---

## Table of Contents

1. [What is GNPS Local?](#1-what-is-gnps-local)
2. [Before You Start: Prerequisites](#2-before-you-start-prerequisites)
3. [Step-by-Step Installation](#3-step-by-step-installation)
   - [3a. Enable WSL2 on Windows 11](#3a-enable-wsl2-on-windows-11)
   - [3b. Install Ubuntu 24.04](#3b-install-ubuntu-2404)
   - [3c. Install Conda (Miniconda)](#3c-install-conda-miniconda)
   - [3d. Get the GNPS Local Code](#3d-get-the-gnps-local-code)
   - [3e. Create the Python Environment](#3e-create-the-python-environment)
   - [3f. Start the Server](#3f-start-the-server)
   - [3g. Updates](3g-updates)
4. [Quick Start: Your First Analysis](#4-quick-start-your-first-analysis)
   - [4a. Prepare Your Data](#4a-prepare-your-data)
   - [4b. Submit a Job](#4b-submit-a-job)
   - [4c. Monitor Progress](#4c-monitor-progress)
   - [4d. Download and View Results](#4d-download-and-view-results)
5. [Understanding Your Results](#5-understanding-your-results)
6. [Troubleshooting & FAQ](#6-troubleshooting--faq)
7. [Workflow Details](#7-workflow-details-for-the-curious)
8. [Data Format Reference](#8-data-format-reference)
9. [Next Steps & Advanced Usage](#9-next-steps--advanced-usage)

---

## 1. What is GNPS Local?

GNPS Local is an offline version of the GNPS (Global Natural Products Social Molecular Networking) platform — the widely-used tool for annotating small molecules in MS/MS metabolomics data. Where the original GNPS ran on cloud servers at UC San Diego, GNPS Local runs entirely on your own Windows machine, with no internet connection needed once it is set up.

The core workflow supported is **Feature-Based Molecular Networking (FBMN)**. You bring your MS/MS spectra and a feature quantification table (from MZmine, XCMS, MS-DIAL, or similar), and GNPS Local builds a molecular network: a visual map in which each node is a detected feature and edges connect features with similar fragmentation patterns. Nodes that match known compounds in the spectral library are annotated automatically.

This tool is designed for researchers who already understand molecular networking concepts and want results without waiting for cloud job queues, without sharing data externally, or without an internet connection. Think of it as running the GNPS analysis server on your own laptop — same science, same outputs, fully local.

---

## 2. Before You Start: Prerequisites

Before installing, confirm the following:

- [ ] **Windows 11** (Home, Pro, or Enterprise — all editions support WSL2)
- [ ] **Administrator access** to your Windows account (needed for WSL2 setup)
- [ ] **~20 GB of free disk space** (for Linux environment, conda, workflow tools, and your data)
- [ ] **Virtualization enabled in BIOS/UEFI** — most modern laptops have this on by default; see [Troubleshooting](#installation-issues) if unsure
- [ ] **Internet connection** for the initial setup (you can work offline afterward)

> **No prior Linux or command-line experience required.** The steps below include every command you need to copy and paste.

---

## 3. Step-by-Step Installation

### 3a. Enable WSL2 on Windows 11

**What is WSL2?** Think of it as a lightweight Linux computer running invisibly inside Windows. GNPS Local's analysis tools are Linux programs, so they need this Linux layer to run. You do not need to understand Linux to use it — you just need it running in the background.

**Step 1:** Open the Start menu, search for **PowerShell**, right-click it, and select **"Run as administrator"**.

**Step 2:** Copy and paste this command, then press Enter:

```powershell
wsl --install
```

**What you should see:**

```
Installing: Virtual Machine Platform
Virtual Machine Platform has been installed.
Installing: Windows Subsystem for Linux
Windows Subsystem for Linux has been installed.
Installing: Ubuntu
Ubuntu has been installed.
The requested operation is successful.
```

**Step 3:** **Restart your computer** when prompted. This is required.

> **If you see an error like "WSL 2 requires an update to its kernel component"**, run this additional command after the restart:
> ```powershell
> wsl --update
> ```

> **If you see "Virtualization is not enabled"**, your computer's BIOS needs a small change — see [Troubleshooting](#installation-issues).

---

### 3b. Install Ubuntu 24.04

After your restart, Ubuntu may open automatically and ask you to set up a username and password. If it does not open automatically:

1. Open the **Start menu** and search for **Ubuntu**.
2. Click **Ubuntu** (or **Ubuntu 24.04**) to open the Linux terminal.

**Set up your Linux username and password:**

```
Enter new UNIX username: yourusername
New password: (type a password — it won't show as you type, that's normal)
Retype new password:
passwd: password updated successfully
```

> **Remember this password** — you will need it occasionally for system commands.

**Verify WSL2 is running correctly.** In PowerShell (not Ubuntu), run:

```powershell
wsl --list --verbose
```

You should see output like:

```
  NAME            STATE           VERSION
* Ubuntu-24.04    Running         2
```

The `VERSION 2` confirms WSL2 is active. You are ready to proceed.

---

### 3c. Install Conda (Miniconda)

Conda is a tool that manages Python packages — think of it as an app store for scientific Python software that keeps everything neatly organized so different tools don't conflict with each other.

Open your **Ubuntu terminal** and run these commands one at a time:

**Download the installer:**

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
```

**Run the installer:**

```bash
bash ~/miniconda.sh
```

- Press **Enter** to scroll through the license agreement.
- Type `yes` to accept the license.
- Press **Enter** to accept the default install location (`/home/yourusername/miniconda3`).
- Type `yes` when asked to initialize conda.

**Apply the changes:**

```bash
source ~/.bashrc
```

**Verify it worked:**

```bash
conda --version
```

You should see something like `conda 24.x.x`. If you see "command not found", close and reopen the Ubuntu terminal and try again.

---

### 3d. Get the GNPS Local Code

You have two options: **GitHub Desktop (recommended)** or **ZIP download**. GitHub Desktop makes it easy to download the code and receive updates when new versions are released — no command line required.

#### Option 1: GitHub Desktop (Recommended)

**Why use this?** GitHub Desktop is a simple graphical tool that keeps your local code synchronized with the latest version. When updates are released, you can fetch them with one click instead of re-downloading everything.

**Step 1:** Download and install **GitHub Desktop** from [https://desktop.github.com](https://desktop.github.com). Sign in with your GitHub account (create a free account if you don't have one).

**Step 2:** Visit the GNPS Local repository on GitHub and click **Fork** in the top-right corner. This creates a personal copy under your account — you now have your own version that you can sync.

**Step 3:** In GitHub Desktop, go to **File → Clone Repository**, select your fork of `GNPS_Local`, and choose where to save it — for example, `D:\GNPS_Local`. GitHub Desktop will download all the code automatically.

**Step 4:** Whenever a new version is released, GitHub Desktop will notify you. Click **Fetch origin** and then **Pull** to download the updates. Your local changes (if any) are preserved.

**For use in Ubuntu:**
In your Ubuntu terminal, navigate to the downloaded folder:

```bash
cd /mnt/d/GNPS_Local
```

> **Note:** `/mnt/d/` is how WSL2 sees your `D:\` drive. If your GNPS Workflows folder is on `C:\`, use `/mnt/c/` instead.

---

#### Option 2: ZIP Download (If You Don't Have GitHub)

If you don't have a GitHub account or prefer not to use GitHub Desktop, download the code as a ZIP file instead.

**Step 1:** Visit the GNPS Local GitHub repository and click the green **Code** button, then select **Download ZIP**.

**Step 2:** Unzip the downloaded file on Windows and place the folder in a convenient location, such as `D:\GNPS_Local`.

**Step 3:** In your Ubuntu terminal, navigate to that folder:

```bash
cd /mnt/d/GNPS_Local
```

> **Note:** If your folder is on `C:\` instead of `D:\`, use `/mnt/c/` in the Ubuntu path instead.

**To receive updates later:** You will need to manually download and unzip a new version from GitHub when releases are announced. This is more cumbersome than GitHub Desktop, but it works fine if you prefer to avoid GitHub altogether.

---

### 3e. Create the Python Environment

This step downloads and installs all the Python packages GNPS Local needs. It may take **5–15 minutes** depending on your internet speed — this is the longest step, but you only do it once.

In your Ubuntu terminal, navigate to your project folder:
```bash
cd /mnt/d/GNPS_Local
```

Create the environment using the provided configuration file:

and activate it:
```bash
conda env create -f environment.yml
```
Activate the environment:

```bash
conda activate gnps
```

---

### 3f. Start the Server

Linux uses LF (linefeed) to mark the end of lines in text files. Cloning the repo on Windows, the script may have Windows-style line endings (CRLF) which can cause errors. The `sed` command below converts them to Unix format.

Every time you want to use GNPS Local, you start the server from your Ubuntu terminal. You leave this terminal window open while you work.

**First time only — fix line endings:**

```bash
cd /mnt/d/GNPS_Local/local_runner
sed -i 's/\r$//' run.sh
```

**Then start the server:**

```bash
conda activate gnps
bash run.sh
```

**Expected output:**

```
  GNPS Local
  ────────────────────────────────
  Open in browser: http://localhost:8000
  Jobs stored in:  ~/gnps_jobs/
  Repo at:         /mnt/d/GNPS_Local
  Stop with:       Ctrl+C

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Open your Windows browser (Chrome, Edge, Firefox) and go to **http://localhost:8000**. You should see the GNPS Local home page with three workflow cards.

> **To stop the server:** Press `Ctrl+C` in the Ubuntu terminal.

---

### 3g. Updates

**If you cloned with Git:**
```bash
cd /mnt/d/GNPS_Local
git pull origin main
```

**If you forked the repo:**

Click the **"Sync fork"** button on your GitHub fork, then:
```bash
git pull origin main
```

**After updating:**

You may need to reinstall Python dependencies:
```bash
cd local_runner
conda activate gnps
pip install -r requirements.txt
```

---

## 4. Quick Start: Your First Analysis

### 4a. Prepare Your Data

For Feature-Based Molecular Networking (FBMN), you need three things:

| File | What it is | Where it comes from |
|---|---|---|
| **MS/MS spectra (.mgf)** | Your raw fragmentation spectra, exported from MZmine/XCMS/MS-DIAL | Your feature-finding software |
| **Feature quantification table (.csv)** | A table of detected features with m/z, RT, and intensity per sample | Your feature-finding software |
| **Metadata table (.tsv) — optional** | Sample group assignments (e.g., treatment vs. control) | You create this |

**File format requirements at a glance:**

- The MGF file must have `SCANS=` or `FEATURE_ID=` fields that match the row IDs in your feature table.
- The feature table must have columns named `row ID`, `row m/z`, `row retention time`, plus one `[filename] Peak area` column per sample.
- Metadata must have a `filename` column whose values exactly match the sample file names in your feature table.

See [Section 8](#8-data-format-reference) for detailed column requirements and examples.

---

### 4b. Submit a Job

1. Open **http://localhost:8000** in your browser.
2. Click **"Feature-Based Molecular Networking"** (the primary, recommended workflow).
3. On the submission form:
   - **Input Spectra (MGF):** Click the upload box and select your `.mgf` file.
   - **Quantification Table:** Upload your feature table (`.csv`).
   - **Feature Table Source:** Select the software you used (e.g., MZmine2, MZmine3, MS-DIAL).
   - **Metadata Table (optional):** Upload if you have sample grouping information.
4. The networking and library search parameters are pre-filled with sensible defaults — you do not need to change them for your first run.
5. Optionally fill in a **Job Name** (e.g., "My_Experiment_Pos_Mode") to help identify the job later.
6. Click **"Submit Job"**.

You will be redirected to a job status page automatically.

---

### 4c. Monitor Progress

The job page shows:

- **Status badge** (Queued → Running → Done/Failed) — updates automatically
- **Run Log** — a live stream of every step the pipeline is executing
- **Output Files** — appear here as each step completes

Typical runtimes depend on data size:

| Dataset size | Approximate time |
|---|---|
| <500 features, 1 library | 2–5 minutes |
| 1,000–3,000 features, 1 library | 5–20 minutes |
| >5,000 features | 30+ minutes |

If a step fails, the log will show `STEP FAILED (exit 1)` with an error message. See [Troubleshooting](#runtime-issues) for common causes.

---

### 4d. Download and View Results

When the job shows **Done**, the Output Files panel lists all results. Key files:

| File | What it contains |
|---|---|
| `gnps_molecular_network.graphml` | The molecular network — open this in Cytoscape |
| `clusterinfo_summary_enriched.tsv` | One row per feature: m/z, RT, intensity, library match, component |
| `librarysearch_results_db.tsv` | All library hits with compound names, scores, SMILES |
| `components_table.tsv` | One row per connected network component |
| `networking_pairs_filtered.tsv` | All edges: which features are similar and by how much |

**To visualize the network:**

1. Download and install **Cytoscape** from [https://cytoscape.org](https://cytoscape.org) (free, cross-platform).
2. In Cytoscape: **File → Import → Network from File**, select your `.graphml` file.
3. Each node is a detected feature. Node color can be mapped to compound annotation; edge width to cosine score.

---

## 5. Understanding Your Results

### The Molecular Network

The network is a graph where:

- **Each node** = one MS/MS feature (a detected compound, or candidate compound) from your data
- **Each edge** = a cosine similarity score ≥ 0.7 (by default) between two spectra, meaning those two features probably share structural similarity
- **Connected clusters** = groups of structurally related compounds (e.g., a series of acyl chain variants)
- **Isolated nodes** (no edges) = features with no structurally similar neighbors in your dataset

A node annotated with a compound name (e.g., "Caffeic acid, MQScore=0.85") means that feature's fragmentation pattern closely matched a reference spectrum in the spectral library.

### Library Match Scores

The `MQScore` (Matching Quality Score) ranges from 0 to 1:

- **0.9–1.0**: Very confident match
- **0.7–0.9**: Good match; confirm with accurate mass
- **0.5–0.7**: Tentative match; treat as a lead, not a confirmed ID
- **< 0.5**: Usually not reported (filtered out by default threshold)

### Common Questions

**"Why is my network very sparse with few edges?"**
Most likely causes: cosine threshold too high (try lowering from 0.7 to 0.5), too few matched peaks (try lowering from 6 to 4), or genuine chemical diversity in your sample.

**"Why do I have very few library matches?"**
The GNPS spectral library covers primarily natural products and common metabolites. Novel compounds, lipids with unusual chains, or very small molecules often do not match. This is expected and does not indicate a pipeline error.

**"What does component index mean?"**
Nodes with the same component index belong to the same connected cluster in the network. `-1` means the node is a singleton (no edges).

---

## 6. Troubleshooting & FAQ

### Installation Issues

**"WSL2 won't install — error about virtualization"**
Your computer's CPU virtualization feature is disabled. Restart your computer and enter the BIOS/UEFI settings (usually by pressing F2, F10, Del, or Esc during startup — your computer's manual will specify which). Look for a setting called "Intel Virtualization Technology", "Intel VT-x", "AMD-V", or "SVM Mode" and enable it. Save and restart.

**"conda not found after install"**
Close the Ubuntu terminal completely and reopen it. Conda modifies your shell configuration, and the change only takes effect in a new terminal session. If it still fails, run `source ~/.bashrc` and try again.

**"Permission denied when running run.sh"**
Run this once to make the script executable:
```bash
chmod +x /mnt/d/GNPS_Local/local_runner/run.sh
```

**"The server starts but I can't reach http://localhost:8000"**
Confirm that the Ubuntu terminal shows the `Uvicorn running` line. If it does and the browser still fails, try `http://127.0.0.1:8000` instead.

---

### Runtime Issues

**"Job is stuck on Queued and never starts"**
The server processes jobs in background threads. If the server was stopped and restarted, previously queued jobs will not automatically resume. Use the "Restart" button on the job page, or resubmit.

**"Step FAILED — how do I read the log?"**

The run log output is shown in the UI of every job
```
http://localhost:8000/job/{job_id}
```

The run log is also saved to disk at:
```
~/gnps_jobs/{job_id}/run.log
```
Open it in Ubuntu with:
```bash
cat ~/gnps_jobs/JOBID/run.log | tail -100
```
The relevant error will be near the bottom, under a `STEP FAILED` line.

**"The server won't start — port 8000 is already in use"**
Another process (possibly a previous server instance) is using port 8000. Find and stop it:
```bash
lsof -i :8000
kill -9 <PID shown above>
```
Then restart with `bash run.sh`.

**"Upload fails or the form seems to hang"**
Large MGF files (>500 MB) may take a moment to upload over the localhost connection. Wait 30 seconds before assuming it has failed. The browser's network tab can confirm whether the upload is still in progress.

**"Reformat quantification FAILED — must input exactly 1 spectrum mgf file"**
Your input folder contains more than one file in the spectra folder. Only one MGF file is supported per job. Make sure you are uploading a single merged MGF (not one per sample).

**"My network looks wrong — very dense or all features connected"**
The cosine threshold may be too low. Resubmit with a higher "Cosine Score Threshold" (try 0.7 if you used a lower value). Also check that your MGF scan numbers match the `row ID` column in your feature table exactly.

---

### Getting Help

When reporting a problem, please include:

1. The **Job ID** (shown on the job page, e.g., `a3f9c12b`)
2. The last 50 lines of `~/gnps_jobs/{job_id}/run.log`
3. The name and source of your feature-finding software
4. Approximate number of features and samples

**To restart a failed job from scratch** (same files, same parameters):
Use the **Restart** button on the job page. This clears the output and log and re-runs the full pipeline.

**To delete a job entirely:**

Locate the following in Windows File Explorer
```
\\wsl.localhost\Ubuntu\home\{username}\gnps_jobs
```

This folder stores all job runs by job ID, delete the entire job ID folder to delete a job.

You can also navigate to the above location in Ubuntu and use the following command to delete by job ID.


```bash
rm -rf ~/gnps_jobs/JOBID
```

---

## 7. Workflow Details (For the Curious)

### What FBMN Actually Does

Your data goes through these stages in order:

1. **Metadata merge** — Your sample metadata is loaded and linked to file names.
2. **Input validation** — Column names and file formats are checked; warnings are logged but the pipeline continues.
3. **Quantification reformatting** — Your feature table (MZmine/XCMS/MS-DIAL format) is converted to the internal GNPS format.
4. **Spectra filtering** — Peaks within the precursor isolation window are removed, and a noise filter is applied. This improves cosine score quality.
5. **Molecular networking** — Every pair of spectra is compared by cosine similarity. Pairs above the threshold become edges.
6. **Edge filtering** — Each node keeps only its top-K best edges; components exceeding the maximum size are pruned.
7. **Library search** — Each spectrum is compared against the local GNPS spectral library.
8. **Cluster info summary** — Features, quantification values, and metadata are merged into a single table.
9. **Enrichment** — Library hits and component indices are added to the cluster info table.
10. **GraphML export** — Everything is assembled into a single file readable by Cytoscape.

### Key Parameters and When to Change Them

| Parameter | Default | What it does | When to change |
|---|---|---|---|
| Cosine Score Threshold | 0.7 | Minimum similarity for an edge | Lower to 0.5 for exploratory analysis; raise to 0.85 for validation |
| Min Matched Peaks | 6 | Minimum shared fragment ions for an edge | Lower to 4 for low-quality spectra; raise to 8 for high confidence |
| Top K Edges per Node | 10 | Max neighbors per feature | Lower for cleaner networks; raise for community detection |
| Max Component Size | 100 | Largest allowed cluster | Set to 0 (unlimited) if you want to see full propagation |
| Fragment Tolerance | 0.02 Da | m/z window for matching fragment ions | Raise to 0.05 for ion-trap data; keep at 0.02 for Orbitrap/Q-TOF |

### Current Limitations

- **Analog search** is implemented in the pipeline but awaiting verification.
- **Statistical analysis** (volcano plots, PCoA) requires the `RUN_STATS` parameter and is not yet enabled in the UI.
- **QIIME2 integration** and **ili 3D spatial mapping** are not available in the local version.
- Only **one MGF file** is supported per job (multi-file input must be merged upstream).

---

## 8. Data Format Reference

### Feature Quantification Table

The feature table must be a **comma-separated (.csv)** file with at minimum these columns:

| Column name | Example | Notes |
|---|---|---|
| `row ID` | `1`, `2`, `3` | Integer, must match SCANS= in MGF |
| `row m/z` | `256.0843` | Precursor m/z |
| `row retention time` | `1.245` | In minutes |
| `Sample1.mzML Peak area` | `45231` | One column per sample, exactly this format |

**First three rows example:**
```
row ID,row m/z,row retention time,Sample1.mzML Peak area,Sample2.mzML Peak area
1,256.0843,1.245,45231,12450
2,431.2012,3.812,0,98320
3,189.0558,2.104,22100,22050
```

**Common mistakes:**
- Column headers must be exact (case-sensitive). `Row ID` ≠ `row ID`.
- Sample columns must end in ` Peak area` (with a space before "Peak").
- Empty intensity cells should be `0`, not blank.

---

### Metadata Table

The metadata file must be a **tab-separated (.tsv)** file.

| Column name | Example | Notes |
|---|---|---|
| `filename` | `Sample1.mzML` | Must exactly match feature table sample names |
| `ATTRIBUTE_Group` | `treatment` | Any column starting with `ATTRIBUTE_` becomes a group |

**First three rows example:**
```
filename	ATTRIBUTE_Group	ATTRIBUTE_Timepoint
Sample1.mzML	treatment	early
Sample2.mzML	control	early
Sample3.mzML	treatment	late
```

**Common mistakes:**
- The `filename` column values must exactly match (including extension and case) what appears in the feature table sample column headers.
- Do not use blank cells. Use `N_A` (with an underscore) for missing values.

---

### MS/MS Spectra (MGF)

Your MGF file should be exported directly from your feature-finding software (MZmine "Export feature list as MGF", XCMS, etc.). Each spectrum block must include:

```
BEGIN IONS
SCANS=1
PEPMASS=256.0843
CHARGE=1+
100.2 5432.1
150.3 8921.0
END IONS
```

The `SCANS=` value must match the `row ID` in your feature table.

If your software uses `FEATURE_ID=` instead of `SCANS=`, this is handled automatically for MZmine3 output.

---

## 9. Next Steps & Advanced Usage

### Running Multiple Jobs

GNPS Local supports multiple simultaneous jobs — just submit them from the web UI. Jobs run in background threads and do not block each other. Be aware that large jobs will compete for CPU resources.

### Exporting for External Analysis

- **Cytoscape (.graphml)**: Visualize and style the molecular network. The Cytoscape GNPS plugin (available in the Cytoscape App Store) can apply pre-built GNPS visual styles.
- **R/Python (.tsv files)**: `clusterinfo_summary_enriched.tsv` and `librarysearch_results_db.tsv` are standard tab-separated tables readable by any statistics tool.
- **Excel**: All `.tsv` output files open directly in Excel via File → Open.

### Checklist Before Analyzing Your Own Data

- [ ] Feature table exported from your software in the correct format (see Section 8)
- [ ] Feature table and MGF from the same software run (scan numbers must match)
- [ ] Metadata filename column exactly matches feature table sample names
- [ ] Single merged MGF file (not one file per sample)
- [ ] GNPS spectral library `.mgf` file(s) placed in `/mnt/d/GNPS_Local/libraries/`

### Spectral Libraries

Download updated GNPS spectral libraries from:
```
https://gnps-external.ucsd.edu/gnpslibrary
```
Place any downloaded `.mgf` files directly into:
```
/mnt/d/GNPS_Local/libraries/
```
The library is loaded automatically for every job.

### What Is Not Yet Implemented

The following features from cloud GNPS are not yet available locally:

- Dereplicator+ (peptidic natural product annotation)
- QIIME2 beta-diversity / PCoA statistics
- ili 3D spatial mapping
- MassIVE dataset search
- Automatic method descriptions

These may be added in future versions.