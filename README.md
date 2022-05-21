# nextstrain.org/monkeypox

This is the [Nextstrain](https://nextstrain.org) build for monkeypox virus. This build is currently
work-in-progress and is not yet publicly visible.

## Usage

Copy input data with:
```
mkdir -p data/
cp -v example_data/* data/
```
Add any additional sequences and metadata in separate fasta or metadata-tsv files to `data`, respectively.

Run pipeline with:
```
snakemake -j 1 -p --configfile=config/config.yaml
```
View results with:
```
auspice view --datasetDir auspice/
```
or with:
```
nextstrain view auspice/
```

## Configuration

Configuration takes place the `config/config.yml`.
The analysis pipeline is contained in `workflow/snakemake_rule/core.smk`.
This can be read top-to-bottom, each rule specifies its file inputs and output and pulls its parameters from `config`.
There is little redirection and each rule should be able to be reasoned with on its own.

## Input data

### GenBank data

Input data is downloaded from [ViPR Poxviridae resource](https://www.viprbrc.org/brc/home.spg?decorator=pox).
- Subfamily: Chordopoxvirinae
- Genus: Orthopoxvirus
- Species: Monkeypox virus

Download Genome FASTA, select custom format, and choose the following fields in this order:
1. Strain name
2. GenBank accession
3. Country
4. Date
5. Host

This downloads the file `GenomicFastaResults.fasta`. Parse this file into sequences and metadata using:
```
augur parse \
 --sequences example_data/GenomicFastaResults.fasta \
 --fields strain accession date country host \
 --output-sequences example_data/sequences.fasta \
 --output-metadata example_data/metadata.tsv
```

ViPR dates are weird with a format of `2006_12_14`. This needs to be manually corrected to `2006-12-14` via regex.

This data is versioned on `example_data/`. The first step in the workflow is to copy `example_data/` to `data/` via:
```
mkdir -p data/
cp -v example_data/* data/
```

### Other data

- [Monkeypox/PT0001/2022](https://virological.org/t/first-draft-genome-sequence-of-monkeypox-virus-associated-with-the-suspected-multi-country-outbreak-may-2022-confirmed-case-in-portugal/799): Download FASTA from Virological post, append to sequences and add the following to metadata:
```
Monkeypox/PT0001/2022	?	2022-05-04	Portugal	Human
```

Data from GenBank follows Open Data principles, such that we can make input data and intermediate
files available for further analysis. Open Data is data that can be freely used, re-used and
redistributed by anyone - subject only, at most, to the requirement to attribute and sharealike.

We gratefully acknowledge the authors, originating and submitting laboratories of the genetic
sequences and metadata for sharing their work in open databases. Please note that although data
generators have generously shared data in an open fashion, that does not mean there should be free
license to publish on this data. Data generators should be cited where possible and collaborations
should be sought in some circumstances. Please try to avoid scooping someone else's work. Reach out
if uncertain. Authors, paper references (where available) and links to GenBank entries are provided
in the metadata file.

## Installation

This pipeline uses:
 - [augur](https://github.com/nextstrain/augur) >v15.0
 - [nextalign](https://github.com/nextstrain/nextclade) >v2.0.0
 - [TreeTime](https://github.com/neherlab/treetime) >v0.9.0
 - [IQTREE](https://github.com/Cibiv/IQ-TREE) >v2.1.2

Augur, TreeTime and IQTREE can be installed as is standard. Nextalign requires installation of latest (not yet released) version.

Clone and checkout `experiment-stripes-updated` branch
```
git clone https://github.com/nextstrain/nextclade
cd nextclade
git checkout experiment-stripes-updated
```

Install `rustup`
```
# Check if rustup (Rust toolchain manager) is installed
which rustup

# If not installed, install (https://rustup.rs/)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add toolchain bin directory to $PATH
export PATH="$PATH:$HOME/.cargo/bin"
```

Building
```
# Build Nextalign in release mode (fast to run, slow to build, no debug info)
cargo build --release --bin nextalign
```

Environment variables
```
echo "DATA_FULL_DOMAIN=https://data.master.clades.nextstrain.org" > .env
```

Test installation
```
./target/release/nextalign run \
  --in-order \
  --include-reference \
  --sequences=data/sars-cov-2/sequences.fasta \
  --reference=data/sars-cov-2/reference.fasta \
  --genemap=data/sars-cov-2/genemap.gff \
  --genes=E,M,N,ORF1a,ORF1b,ORF3a,ORF6,ORF7a,ORF7b,ORF8,ORF9b,S \
  --output-dir=tmp/ \
  --output-basename=nextalign
```

Copy `nextalign` binary to somewhere globally accessible
```
sudo cp target/release/nextalign /usr/local/bin/
```
