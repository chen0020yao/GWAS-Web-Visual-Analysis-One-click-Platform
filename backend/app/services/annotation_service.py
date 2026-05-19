import requests

# 简单缓存（防止频繁请求NCBI）
cache = {}

def query_ncbi_snp(rsid: str):
    if rsid in cache:
        return cache[rsid]

    try:
        url = f"https://api.ncbi.nlm.nih.gov/variation/v0/beta/refsnp/{rsid.replace('rs','')}"
        res = requests.get(url, timeout=5)

        if res.status_code != 200:
            return {"error": "NCBI查询失败"}

        data = res.json()

        gene = "Unknown"
        consequence = "Unknown"

        if "primary_snapshot_data" in data:
            ann = data["primary_snapshot_data"]

            if "allele_annotations" in ann:
                for a in ann["allele_annotations"]:
                    if "assembly_annotation" in a:
                        for aa in a["assembly_annotation"]:
                            if "genes" in aa:
                                gene = aa["genes"][0].get("locus", "Unknown")

        result = {
            "rsid": rsid,
            "gene": gene,
            "consequence": consequence
        }

        cache[rsid] = result
        return result

    except Exception as e:
        return {"error": str(e)}