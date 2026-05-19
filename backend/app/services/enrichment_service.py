import gseapy as gp

# =========================
# GO 富集分析
# =========================
def go_enrichment(gene_list):
    if len(gene_list) == 0:
        return {"error": "no genes"}

    enr = gp.enrichr(
        gene_list=gene_list,
        gene_sets="GO_Biological_Process_2023",
        organism="Human",
        outdir=None
    )

    return enr.results.head(20).to_dict("records")


# =========================
# KEGG 富集分析
# =========================
def kegg_enrichment(gene_list):
    if len(gene_list) == 0:
        return {"error": "no genes"}

    enr = gp.enrichr(
        gene_list=gene_list,
        gene_sets="KEGG_2021_Human",
        organism="Human",
        outdir=None
    )

    return enr.results.head(20).to_dict("records")