from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, List

import pandas as pd
import requests


DOI_RE = re.compile(r"10\.\d{4,9}/[^\s]+", re.IGNORECASE)


@dataclass
class OAResult:
    status: str                 # downloaded | no_doi | oa_no_pdf | restricted | error
    source: str = ""            # unpaywall | openalex | ""
    pdf_url: str = ""
    note: str = ""              # error message or reason
    is_oa: Optional[bool] = None


class OAPDFFetcher:
    """
    Legal OA PDF fetcher (no Sci-Hub).
    - Uses Unpaywall (primary) and OpenAlex (fallback).
    - Works over a pandas DataFrame.
    """

    def __init__(
        self,
        email_for_unpaywall: str,
        outdir: str = "oa_pdfs",
        doi_col: str = "doi",
        id_col: str = "ID",
        user_agent: str = "oa-pdf-fetcher/1.0 (+contact: you@example.org)",
        request_timeout_s: int = 25,
        sleep_s: float = 0.2,
    ):
        self.email = email_for_unpaywall
        self.outdir = outdir
        self.doi_col = doi_col
        self.id_col = id_col
        self.user_agent = user_agent
        self.timeout = request_timeout_s
        self.sleep_s = sleep_s

        os.makedirs(self.outdir, exist_ok=True)

    @staticmethod
    def _normalize_doi(raw: str) -> str:
        s = str(raw).strip()
        s = s.replace("https://doi.org/", "").replace("http://doi.org/", "")
        s = s.replace("doi:", "").strip()
        # if line contains extra text, try extract DOI
        m = DOI_RE.search(s)
        return m.group(0) if m else s

    def _get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        r = requests.get(
            url,
            params=params,
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def _unpaywall(self, doi: str) -> Tuple[Optional[str], Optional[bool]]:
        """
        Returns (pdf_url, is_oa) when available.
        """
        url = f"https://api.unpaywall.org/v2/{doi}"
        data = self._get_json(url, params={"email": self.email})

        is_oa = data.get("is_oa")
        best = data.get("best_oa_location") or {}
        pdf = best.get("url_for_pdf")

        if pdf:
            return pdf, is_oa

        for loc in data.get("oa_locations") or []:
            pdf = loc.get("url_for_pdf")
            if pdf:
                return pdf, is_oa

        return None, is_oa

    def _openalex(self, doi: str) -> Tuple[Optional[str], Optional[bool]]:
        """
        Returns (pdf_url, is_oa) when available.
        """
        url = "https://api.openalex.org/works/https://doi.org/" + doi
        data = self._get_json(url)

        oa = data.get("open_access") or {}
        is_oa = oa.get("is_oa")

        # Prefer direct pdf_url locations
        locations = []
        if data.get("primary_location"):
            locations.append(data["primary_location"])
        locations.extend(data.get("locations") or [])

        for loc in locations:
            if not loc:
                continue
            pdf = loc.get("pdf_url")
            if pdf:
                return pdf, is_oa

        return None, is_oa

    def _download_pdf(self, pdf_url: str, out_path: str) -> None:
        with requests.get(
            pdf_url,
            stream=True,
            headers={"User-Agent": self.user_agent},
            timeout=max(self.timeout, 60),
            allow_redirects=True,
        ) as r:
            r.raise_for_status()
            ctype = (r.headers.get("Content-Type") or "").lower()

            # Some servers mislabel content-type; verify header magic if needed
            first = next(r.iter_content(chunk_size=2048), b"")
            if (("pdf" not in ctype) and (not pdf_url.lower().endswith(".pdf")) and (not first.startswith(b"%PDF"))):
                raise ValueError(f"URL does not appear to be a PDF (Content-Type={ctype})")

            with open(out_path, "wb") as f:
                f.write(first)
                for chunk in r.iter_content(chunk_size=1024 * 128):
                    if chunk:
                        f.write(chunk)

    def fetch_pdf_for_doi(self, doi: str, file_stem: str) -> OAResult:
        """
        Tries Unpaywall then OpenAlex. Writes <outdir>/<file_stem>.pdf on success.
        """
        if doi is None or str(doi).strip() == "" or str(doi).strip().lower() == "nan":
            return OAResult(status="no_doi", note="Missing DOI.", is_oa=None)

        doi_norm = self._normalize_doi(doi)
        if not doi_norm.lower().startswith("10."):
            # Treat as missing/invalid DOI rather than error
            return OAResult(status="no_doi", note="Invalid DOI format.", is_oa=None)

        try:
            pdf_url, is_oa = self._unpaywall(doi_norm)
            source = "unpaywall"
            if not pdf_url:
                pdf_url, is_oa_oa = self._openalex(doi_norm)
                source = "openalex" if pdf_url else ""
                # if OpenAlex returns is_oa but Unpaywall did too, prefer Unpaywall’s value when present
                if is_oa is None:
                    is_oa = is_oa_oa

            if not pdf_url:
                # Decide reason: OA but no direct pdf vs restricted
                if is_oa is True:
                    return OAResult(status="oa_no_pdf", source=source, is_oa=True, note="Open access but no direct PDF URL.")
                if is_oa is False:
                    return OAResult(status="restricted", source=source, is_oa=False, note="Not open access (paywalled/restricted).")
                return OAResult(status="restricted", source=source, is_oa=None, note="No OA PDF link found.")

            out_path = os.path.join(self.outdir, f"{file_stem}.pdf")
            self._download_pdf(pdf_url, out_path)
            time.sleep(self.sleep_s)
            return OAResult(status="downloaded", source=source, pdf_url=pdf_url, is_oa=is_oa)

        except Exception as e:
            return OAResult(status="error", note=str(e))

    def process_dataframe(
        self,
        df: pd.DataFrame,
        *,
        status_col: str = "pdf_status",
        source_col: str = "pdf_source",
        reason_col: str = "pdf_reason",
        url_col: str = "pdf_url",
        overwrite_existing: bool = False,
    ) -> pd.DataFrame:
        """
        Returns a copy of df with new columns:
          - pdf_status: downloaded | no_doi | oa_no_pdf | restricted | error
          - pdf_source: unpaywall | openalex | ""
          - pdf_reason: extra detail
          - pdf_url: the URL used (when available)
        Saves PDFs as <outdir>/<ID>.pdf
        """
        if self.doi_col not in df.columns:
            raise KeyError(f"DataFrame missing DOI column '{self.doi_col}'")
        if self.id_col not in df.columns:
            raise KeyError(f"DataFrame missing ID column '{self.id_col}'")

        out = df.copy()

        # Ensure columns exist
        for c in [status_col, source_col, reason_col, url_col]:
            if c not in out.columns:
                out[c] = ""

        for idx, row in out.iterrows():
            doc_id = row.get(self.id_col)
            doi = row.get(self.doi_col)

            # Define filename stem from ID
            if doc_id is None or str(doc_id).strip() == "" or str(doc_id).strip().lower() == "nan":
                # If ID is missing, still process but avoid writing ambiguous filename
                file_stem = f"row_{idx}"
                id_note = "Missing ID; used row index as filename."
            else:
                # sanitize filename
                file_stem = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(doc_id).strip())
                id_note = ""

            out_path = os.path.join(self.outdir, f"{file_stem}.pdf")
            if (not overwrite_existing) and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                out.at[idx, status_col] = "downloaded"
                out.at[idx, source_col] = "existing"
                out.at[idx, reason_col] = "File already exists."
                out.at[idx, url_col] = ""
                continue

            res = self.fetch_pdf_for_doi(doi=str(doi) if doi is not None else "", file_stem=file_stem)

            out.at[idx, status_col] = res.status
            out.at[idx, source_col] = res.source
            out.at[idx, reason_col] = (id_note + " " + res.note).strip()
            out.at[idx, url_col] = res.pdf_url

        return out


# -------------------------
# CLI usage
# -------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch OA PDFs via Unpaywall/OpenAlex and update a CSV.")
    parser.add_argument("--csv", default="articles_screened.csv", help="Input CSV path.")
    parser.add_argument("--email", required=True, help="Contact email for Unpaywall.")
    parser.add_argument("--outdir", default="articulos_descargados", help="Output directory for PDFs.")
    parser.add_argument("--id-col", default="ID_articulo", help="Column name for document ID.")
    parser.add_argument("--doi-col", default="doi", help="Column name for DOI.")
    parser.add_argument("--status-col", default="Estado_acceso", help="Column name to update with access status.")
    parser.add_argument("--decision-col", default="Decisión_final", help="Column with inclusion decision.")
    parser.add_argument("--overwrite-existing", action="store_true", help="Overwrite existing PDFs.")
    args = parser.parse_args()

    def map_pdf_status(pdf_status: str) -> str:
        status = (pdf_status or "").strip()
        if status == "downloaded":
            return "Descargado"
        if status == "oa_no_pdf":
            return "Sin acceso (OA)"
        if status == "restricted":
            return "Sin acceso (Restringido)"
        if status == "no_doi":
            return "Sin acceso (Sin DOI)"
        if status == "error":
            return "Error"
        return ""

    def merge_status(current: str, candidate: str) -> str:
        # Keep the most informative/highest-precedence status
        order = {
            "Descargado": 4,
            "Sin acceso (OA)": 3,
            "Sin acceso (Restringido)": 2,
            "Sin acceso (Sin DOI)": 1,
            "Error": 0,
            "Pendiente": 0,
            "": 0,
        }
        cur = (current or "").strip()
        cand = (candidate or "").strip()
        return cand if order.get(cand, 0) >= order.get(cur, 0) else cur

    df = pd.read_csv(args.csv, keep_default_na=False)

    if args.status_col not in df.columns:
        df[args.status_col] = ""

    if args.decision_col in df.columns:
        decision = df[args.decision_col].astype(str).str.strip().str.lower()
        mask_incluir = decision == "incluir"
        df.loc[~mask_incluir, args.status_col] = "No aplica"
    else:
        mask_incluir = pd.Series([True] * len(df), index=df.index)

    fetcher = OAPDFFetcher(
        email_for_unpaywall=args.email,
        outdir=args.outdir,
        doi_col=args.doi_col,
        id_col=args.id_col,
        user_agent=f"oa-pdf-fetcher/1.0 (+contact: {args.email})",
    )

    df_in = df.loc[mask_incluir].copy()
    df_in = fetcher.process_dataframe(
        df_in,
        status_col="pdf_status",
        source_col="pdf_source",
        reason_col="pdf_reason",
        url_col="pdf_url",
        overwrite_existing=args.overwrite_existing,
    )

    # Merge results back into original dataframe
    for idx, row in df_in.iterrows():
        new_status = map_pdf_status(row.get("pdf_status", ""))
        df.at[idx, args.status_col] = merge_status(df.at[idx, args.status_col], new_status)

    # Optional: keep trace columns for auditing
    for c in ["pdf_status", "pdf_source", "pdf_reason", "pdf_url"]:
        df[c] = df_in.get(c, "")

    df.to_csv(args.csv, index=False)
