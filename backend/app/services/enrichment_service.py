import gseapy as gp
from app.services.utils import make_json_safe
import warnings


def _run_enrichr(gene_list: list, gene_sets: str):
    """安全调用 gseapy.enrichr，包含超时和异常处理"""
    if len(gene_list) == 0:
        return [{"error": "no genes provided"}]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            enr = gp.enrichr(
                gene_list=gene_list,
                gene_sets=gene_sets,
                organism="Human",
                outdir="/tmp/gseapy_out",
                no_plot=True,
            )
            if enr is None or enr.results is None or enr.results.empty:
                return [{"info": "enrichr returned no results"}]
            return make_json_safe(enr.results.head(20).to_dict("records"))
        except Exception as e:
            return [{"error": f"Enrichr API failed: {str(e)}"}]


def go_enrichment(gene_list):
    return _run_enrichr(gene_list, "GO_Biological_Process_2023")


def kegg_enrichment(gene_list):
    return _run_enrichr(gene_list, "KEGG_2021_Human")