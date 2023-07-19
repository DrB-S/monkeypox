rule update_example_data:
    """This updates the files under example_data/ based on latest available data from data.nextstrain.org.

    The subset of data is generated by an augur filter call which:
    - sets the subsampling size to 50
    - includes the root (defined in config but hardcoded here)
    - ensures all clades and lineages are accounted for using --group-by
    """
    message:
        "Update example data"
    input:
        sequences="data/sequences.fasta",
        metadata="data/metadata.tsv",
    output:
        sequences="example_data/sequences.fasta",
        metadata="example_data/metadata.tsv",
    params:
        strain_id=config["strain_id_field"],
    shell:
        """
        augur filter \
            --metadata {input.metadata} \
            --metadata-id-columns {params.strain_id} \
            --sequences {input.sequences} \
            --include-where strain=MK783032 strain=MK783030 \
            --group-by clade lineage \
            --subsample-max-sequences 50 \
            --subsample-seed 0 \
            --output-metadata {output.metadata} \
            --output-sequences {output.sequences}
        """
