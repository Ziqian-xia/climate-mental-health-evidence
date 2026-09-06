# First-pass full-corpus results

These are published snapshots. The full CSV and JSON are GitHub Release assets.

| File | Scope | Location |
| --- | --- | --- |
| result.csv | All 131,468 records | [Download round1-result.csv](https://github.com/Ziqian-xia/climate-mental-health-evidence/releases/download/final-screening-v1/round1-result.csv) |
| review.csv | The 7,217 REVIEW records in this snapshot | [Open local review.csv](review.csv) |
| result.json | All records, retained responses, and provenance | [Download round1-result.json.gz](https://github.com/Ziqian-xia/climate-mental-health-evidence/releases/download/final-screening-v1/round1-result.json.gz) |

Counts: EXCLUDE 123,543; INCLUDE 708; REVIEW 7,217.
The CSV has the original 12 public columns. No token or attempt-count columns were added.
The compressed JSON is a lossless copy of the original result.json.

The filenames of Release downloads have a prefix to distinguish the two rounds.
The JSON's csv_sha256 keys refer to the original filenames result.csv and review.csv;
renaming a download does not change its content hash.

Uncompressed JSON SHA256: 5e17a7006d6c0f96e64809d230a6119209cccdfce4cfc8a2f069129d90a3c023

Full CSV SHA256: dfbe8be159a258fbc794e129f371394e3e53c9f117082ce0e301ad54517600ea

Compressed JSON SHA256: beab7d709c40882f5a77c665350683d0d1272ed7572a6eeba83cb30996d8d394

REVIEW CSV SHA256: 4513075bba48f69cc658c3f2abe7a1cc709cd84ff3033f9118da20cc8442093a

The [Release](https://github.com/Ziqian-xia/climate-mental-health-evidence/releases/tag/final-screening-v1) and its download links become available when the
maintainer publishes the supplied attachments under tag final-screening-v1.
