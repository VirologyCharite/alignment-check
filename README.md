# alignment-check

Assess a multiple sequence alignment (MSA) FASTA file for errors and
anomalies, and gather general information about it, producing a single
self-contained HTML report with interactive [Plotly](https://plotly.com/python/)
plots.

## Installation

### With pip

```sh
pip install alignment-check
```

### With uv

To use it as a one-off command without installing it into a project:

```sh
uvx alignment-check ...
```

To add it as a dependency of a project:

```sh
uv add alignment-check
```

## Usage

```sh
alignment-check alignment.fasta -o report.html
```

If no input file is given, the alignment is read from standard input:

```sh
cat alignment.fasta | alignment-check -o report.html
```

By default, the report is written to `alignment_check_report.html` in the
current directory.

### Options

| Option | Description |
| --- | --- |
| `-o`, `--output PATH` | Where to write the HTML report (default: `alignment_check_report.html`). |
| `--gap-chars CHARS` | Characters treated as alignment gaps (default: `-.?`). |
| `--allow-all-id-chars` | Disable the check for sequence IDs containing characters that can break downstream tools. |
| `--n2` | Enable analyses that take O(n²) time in the number of sequences (currently: the pairwise identity histogram). Skipped by default. |
| `--gc-low`, `--gc-high FLOAT` | Fixed thresholds for flagging unusual G/C content (default: statistical, based on the alignment's own distribution). |
| `--gap-count-low`, `--gap-count-high FLOAT` | Fixed thresholds for flagging an unusual gap count. |
| `--n-count-low`, `--n-count-high FLOAT` | Fixed thresholds for flagging an unusual N count. |
| `--ambiguous-count-low`, `--ambiguous-count-high FLOAT` | Fixed thresholds for flagging an unusual ambiguous-nucleotide-code count. |
| `--indel-minority-fraction FLOAT` | A column's minority group must be smaller than this fraction of all sequences to be a candidate indel column (default: `0.1`). |
| `--indel-min-length INT` | Minimum number of consecutive columns to report as an indel region (default: `10`). |
| `--long-stretch-fraction FLOAT` | Minimum length, as a fraction of sequence length, of a run of ambiguous/N characters to flag (default: `0.1`). |

Run `alignment-check --help` for the full, current list.

## What gets checked

**Errors** (structural problems with the input): the file isn't FASTA, it
doesn't exist, it's empty, it has only one sequence, sequences aren't all
the same length, a sequence is entirely gaps or 'N's, nucleotide and
protein sequences are mixed together, duplicate or empty sequence IDs,
sequence IDs with problematic characters, and sequence characters that
aren't valid nucleotide/protein/gap codes.

**Anomalies** (statistical or structural oddities, once the input is
clean): sequences with unusual G/C content, gap count, N count, or
ambiguous-code count (each flagged as a statistical outlier by default,
or against a fixed threshold if given); gap-only columns; contiguous
insertion/deletion regions found in only a minority of sequences; and
long localized runs of ambiguous/N characters within an otherwise clean
sequence.

Sequences flagged as all-gap or all-N are excluded from every check and
plot beyond the error that flags them.

**Info** (general information, some as interactive plots): sequence
count and length; a sortable per-sequence table (length, gap count,
G/C%, N count, ambiguous-code count); and, across the alignment, plots
of per-site gap fraction, per-site majority-character frequency,
per-site nucleotide ambiguity (nucleotide alignments only), per-site
homogeneity, and (with `--n2`) the distribution of pairwise sequence
identities.

## Development

```sh
uv sync
uv run pytest
```

Library code lives under `src/alignment_check/`, one check or info
function per file (`checks/` for errors and anomalies, `info/` for
general information and plots), each with a matching test file under
`tests/`. The CLI script (`src/alignment_check/cli/alignment_check.py`)
is the only place that wires these functions together.

### Pre-commit hook

A `.pre-commit-config.yaml` runs the test suite before each commit.
Install it once after cloning:

```sh
uv run pre-commit install
```

Committing the config file alone doesn't activate anything; each clone
needs to run the command above once.

### Versioning and releases

The package version is derived automatically from git tags (via
`uv-dynamic-versioning`) — there is nothing to bump by hand in
`pyproject.toml`. Tags must look like `vX.Y.Z` (e.g. `v0.2.0`).

To publish a new version to PyPI:

1. Push a tag: `git tag v0.2.0 && git push origin v0.2.0`.
2. Create a Release from that tag on the GitHub site (Releases ->
   Draft a new release).
3. Publishing the release triggers `.github/workflows/release.yml`,
   which runs the tests, builds the package, and publishes it to PyPI
   using [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
   (no API token needed).

Before the first release, a maintainer needs to:

- Add a Trusted Publisher for this repository on the PyPI project's
  "Publishing" settings page.
- Create a `pypi` environment under the repository's Settings ->
  Environments (matching the `environment: name: pypi` used in
  `release.yml`).

Every push to `main`, and every pull request, runs the test suite via
`.github/workflows/test.yml`.
