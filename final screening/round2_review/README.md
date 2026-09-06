# Pass 2: reassessment of the original REVIEW set

Use **rerun_review.py** for this pass. The retained run.py is an unchanged
dependency/source snapshot and is not the entry point for REVIEW reassessment.

- [Complete procedure and final counts](../README.md)
- [Run, resume, and export instructions](START_REVIEW.md)
- [Final merged full-corpus results](results/README.md)

The input selection is the 7,217 REVIEW records from the frozen first-pass
result.json. Only the router prompt changed between the two passes. All other
prompts, eligibility criteria, and the original screening engine are unchanged.

The final merged corpus contains all 131,468 records, including the 124,251
original INCLUDE/EXCLUDE records preserved from the first pass.

The executable source and prompts are identical to those used in the completed
second pass. Documentation and package checksums were updated for this
publication layout. The published result JSON retains its original execution
metadata unchanged; do not rewrite that metadata to match documentation hashes.
