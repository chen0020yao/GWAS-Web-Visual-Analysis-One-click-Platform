"""
SNP → 基因映射服务
- 方案 A: mygene 批量查询 (rs ID → gene symbol)
- 方案 B: 基因组位置映射 (CHR:BP → gene, 本地 BED 文件)
- 策略: 先用 mygene，未命中的用 BED 位置兜底
"""
import os
import pandas as pd
import numpy as np
import requests
import gzip
from io import BytesIO

BED_URL = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/refGene.txt.gz"
BED_LOCAL = os.path.join(os.path.dirname(__file__), "..", "data", "refGene.bed")


class GeneMapper:
    def __init__(self):
        self._mg = None
        self._bed = None
        self._ensure_bed()

    # =====================
    # mygene 懒加载
    # =====================
    @property
    def mg(self):
        if self._mg is None:
            try:
                import mygene
                self._mg = mygene.MyGeneInfo()
            except ImportError:
                self._mg = False  # 标记不可用
        return self._mg if self._mg is not False else None

    # =====================
    # BED 文件加载 / 下载
    # =====================
    def _ensure_bed(self):
        if not os.path.exists(BED_LOCAL):
            self._download_bed()
        if os.path.exists(BED_LOCAL):
            self._bed = pd.read_csv(
                BED_LOCAL, sep="\t", header=None,
                names=["chr", "start", "end", "gene"],
                dtype={"chr": str, "start": int, "end": int, "gene": str}
            )
            self._bed["chr"] = self._bed["chr"].str.replace("chr", "", regex=False)

    def _download_bed(self):
        os.makedirs(os.path.dirname(BED_LOCAL), exist_ok=True)
        try:
            resp = requests.get(BED_URL, timeout=120)
            if resp.status_code == 200:
                # refGene.txt.gz 是 gzip 压缩的 TSV
                with gzip.GzipFile(fileobj=BytesIO(resp.content)) as gz:
                    lines = gz.read().decode("utf-8").splitlines()
                with open(BED_LOCAL, "w") as f:
                    for line in lines:
                        cols = line.strip().split("\t")
                        if len(cols) < 13:
                            continue
                        # cols[0]=bin, [1]=name, [2]=chrom, [3]=strand,
                        # [4]=txStart, [5]=txEnd, [9]=exonCount, [11]=geneSymbol
                        chrom = cols[2]
                        start = cols[4]
                        end = cols[5]
                        gene = cols[12]  # name2 / gene symbol
                        if gene == "":
                            gene = cols[1]  # fallback to transcript name
                        f.write(f"{chrom}\t{start}\t{end}\t{gene}\n")
                print(f"[GeneMapper] BED file downloaded: {BED_LOCAL}")
            else:
                print(f"[GeneMapper] BED download failed, HTTP {resp.status_code}")
        except Exception as e:
            print(f"[GeneMapper] BED download error: {e}")

    # =====================
    # 主入口: SNP DataFrame → 基因列表
    # =====================
    def map_dataframe(self, sig_df: pd.DataFrame) -> list:
        """
        sig_df: 显著 SNP，至少含 ID (rs号), CHR, BP 三列
        返回: 基因符号列表 (去重, 非空)
        """
        results = {}  # rsid → gene_symbol

        # --- A: mygene 批量查询 ---
        rsids = sig_df["ID"].astype(str).tolist()
        if self.mg:
            try:
                mg_out = self.mg.querymany(
                    rsids,
                    scopes="dbsnp.rsid",
                    fields="symbol",
                    species="human",
                    returnall=True,
                )
                for entry in mg_out.get("out", []):
                    rid = str(entry.get("query", ""))
                    sym = entry.get("symbol")
                    if sym and rid:
                        results[rid] = sym
            except Exception as e:
                print(f"[GeneMapper] mygene error: {e}")

        # --- B: 位置映射兜底 ---
        unmapped = sig_df[~sig_df["ID"].astype(str).isin(results.keys())]
        if self._bed is not None and len(unmapped) > 0:
            for _, row in unmapped.iterrows():
                rsid = str(row["ID"])
                chrom = str(int(row["CHR"]))
                pos = int(row["BP"])
                hits = self._bed[
                    (self._bed["chr"] == chrom) &
                    (self._bed["start"] <= pos) &
                    (self._bed["end"] >= pos)
                ]
                if len(hits) > 0:
                    results[rsid] = hits.iloc[0]["gene"]

        # 去重，过滤无效值，返回基因符号列表
        genes = list(set(
            g for g in results.values()
            if g and g not in ("", "Unknown", "unknown", ".")
        ))
        return genes


# 单例
_mapper = None


def get_gene_mapper() -> GeneMapper:
    global _mapper
    if _mapper is None:
        _mapper = GeneMapper()
    return _mapper
