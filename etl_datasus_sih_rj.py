"""ETL DATASUS SIH/SUS — internações hospitalares do RJ em 2025 (Produto 4 / DS-01).

Uso:  python scripts/dados/etl_datasus_sih_rj.py
Pipeline (metodologia do artigo IND-02): extração via FTP oficial do DATASUS →
leitura dos .dbc (pyreaddbc) → limpeza/padronização (município IBGE, especialidade,
capítulo CID-10) → agregações analíticas em CSV UTF-8.

Saídas em producao/p04-bases-abertas/DS-01/clean/:
  sih_rj_2025_municipio_mes_especialidade.csv  (fato principal)
  sih_rj_2025_capitulo_cid_mes.csv             (morbidade por capítulo CID-10)
  sih_rj_2025_resumo_mensal.csv                (série estadual)
Cache bruto (não versionado): producao/p04-bases-abertas/DS-01/raw/*.dbc
"""
import io
import json
import sys
import urllib.request
from ftplib import FTP
from pathlib import Path

import pandas as pd
from pyreaddbc import dbc2dbf
from dbfread import DBF

RAIZ = Path(__file__).resolve().parents[2]
DS = RAIZ / "producao" / "p04-bases-abertas" / "DS-01"
RAW, CLEAN = DS / "raw", DS / "clean"
MESES = [f"{m:02d}" for m in range(1, 13)]
FTP_DIR = "/dissemin/publicos/SIHSUS/200801_/Dados"

ESPECIALIDADES = {
    "01": "Cirúrgico", "02": "Obstétrico", "03": "Clínico", "04": "Crônicos",
    "05": "Psiquiatria", "06": "Pneumologia sanitária", "07": "Pediátrico",
    "08": "Reabilitação", "09": "Leito-dia cirúrgico", "10": "Leito-dia AIDS",
    "11": "Leito-dia fibrose cística", "12": "Leito-dia intercorrências",
    "13": "Leito-dia geriatria", "14": "Leito-dia saúde mental",
}

CAPITULOS_CID10 = [  # (início, fim, capítulo, descrição curta)
    ("A00", "B99", "I", "Infecciosas e parasitárias"),
    ("C00", "D48", "II", "Neoplasias"),
    ("D50", "D89", "III", "Sangue e imunidade"),
    ("E00", "E90", "IV", "Endócrinas e metabólicas"),
    ("F00", "F99", "V", "Transtornos mentais"),
    ("G00", "G99", "VI", "Sistema nervoso"),
    ("H00", "H59", "VII", "Olho e anexos"),
    ("H60", "H95", "VIII", "Ouvido"),
    ("I00", "I99", "IX", "Aparelho circulatório"),
    ("J00", "J99", "X", "Aparelho respiratório"),
    ("K00", "K93", "XI", "Aparelho digestivo"),
    ("L00", "L99", "XII", "Pele e subcutâneo"),
    ("M00", "M99", "XIII", "Osteomuscular"),
    ("N00", "N99", "XIV", "Aparelho geniturinário"),
    ("O00", "O99", "XV", "Gravidez, parto e puerpério"),
    ("P00", "P96", "XVI", "Afecções perinatais"),
    ("Q00", "Q99", "XVII", "Malformações congênitas"),
    ("R00", "R99", "XVIII", "Sintomas e achados anormais"),
    ("S00", "T98", "XIX", "Lesões e envenenamentos"),
    ("V01", "Y98", "XX", "Causas externas"),
    ("Z00", "Z99", "XXI", "Fatores que influenciam a saúde"),
    ("U00", "U99", "XXII", "Códigos para propósitos especiais"),
]


def capitulo_cid(cod: str) -> tuple[str, str]:
    cod = (cod or "").strip().upper()[:3]
    if len(cod) < 3 or not cod[0].isalpha():
        return "ND", "Não informado"
    for ini, fim, cap, desc in CAPITULOS_CID10:
        if ini <= cod <= fim:
            return cap, desc
    return "ND", "Não informado"


def municipios_rj() -> pd.DataFrame:
    """Código IBGE (6 dígitos, como no SIH) -> nome do município."""
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios"
    bruto = urllib.request.urlopen(url, timeout=60).read()
    if bruto[:2] == b"\x1f\x8b":  # gzip
        import gzip
        bruto = gzip.decompress(bruto)
    dados = json.loads(bruto)
    return pd.DataFrame(
        [{"cod_mun": str(m["id"])[:6], "municipio": m["nome"]} for m in dados])


def baixar():
    RAW.mkdir(parents=True, exist_ok=True)
    faltam = [m for m in MESES if not (RAW / f"RDRJ25{m}.dbc").exists()]
    if not faltam:
        return
    ftp = FTP("ftp.datasus.gov.br", timeout=120)
    ftp.login()
    ftp.cwd(FTP_DIR)
    for m in faltam:
        nome = f"RDRJ25{m}.dbc"
        print(f"  baixando {nome}...")
        with open(RAW / nome, "wb") as f:
            ftp.retrbinary(f"RETR {nome}", f.write)
    ftp.quit()


def ler_mes(mes: str) -> pd.DataFrame:
    dbc, dbf = RAW / f"RDRJ25{mes}.dbc", RAW / f"RDRJ25{mes}.dbf"
    if not dbf.exists():
        # a lib C do dbc2dbf não abre caminhos com acentos — converter em pasta ASCII
        import shutil, tempfile
        tmp = Path(tempfile.gettempdir()) / "ted77_dbc"
        tmp.mkdir(exist_ok=True)
        shutil.copy2(dbc, tmp / dbc.name)
        dbc2dbf(str(tmp / dbc.name), str(tmp / dbf.name))
        shutil.move(str(tmp / dbf.name), str(dbf))
        (tmp / dbc.name).unlink()
    cols = ["MUNIC_RES", "ESPEC", "QT_DIARIAS", "VAL_TOT", "MORTE", "DIAG_PRINC", "SEXO"]
    regs = DBF(str(dbf), encoding="latin-1", char_decode_errors="replace")
    df = pd.DataFrame((tuple(r[c] for c in cols) for r in regs), columns=cols)
    df["mes"] = f"2025-{mes}"
    return df


def main():
    print("== download FTP DATASUS ==")
    baixar()
    print("== leitura dos 12 meses ==")
    df = pd.concat([ler_mes(m) for m in MESES], ignore_index=True)
    print(f"  {len(df):,} AIHs lidas")

    # padronização
    df["VAL_TOT"] = pd.to_numeric(df["VAL_TOT"], errors="coerce").fillna(0.0)
    df["QT_DIARIAS"] = pd.to_numeric(df["QT_DIARIAS"], errors="coerce").fillna(0).astype(int)
    df["MORTE"] = pd.to_numeric(df["MORTE"], errors="coerce").fillna(0).astype(int)
    df["especialidade"] = df["ESPEC"].astype(str).str.zfill(2).map(ESPECIALIDADES).fillna("Outros")
    df["sexo"] = df["SEXO"].astype(str).map({"1": "Masculino", "3": "Feminino"}).fillna("Não informado")
    caps = df["DIAG_PRINC"].map(capitulo_cid)
    df["cap_cid"] = caps.str[0]
    df["cap_cid_desc"] = caps.str[1]
    df["cod_mun"] = df["MUNIC_RES"].astype(str).str.zfill(6)

    mun = municipios_rj()
    df = df.merge(mun, on="cod_mun", how="left")
    df["municipio"] = df["municipio"].fillna("Outros estados / ignorado")

    CLEAN.mkdir(parents=True, exist_ok=True)

    # T1 — fato principal: município × mês × especialidade
    t1 = (df.groupby(["cod_mun", "municipio", "mes", "especialidade"], as_index=False)
            .agg(internacoes=("VAL_TOT", "size"),
                 valor_total_brl=("VAL_TOT", "sum"),
                 dias_permanencia=("QT_DIARIAS", "sum"),
                 obitos=("MORTE", "sum")))
    t1["valor_total_brl"] = t1["valor_total_brl"].round(2)
    t1.to_csv(CLEAN / "sih_rj_2025_municipio_mes_especialidade.csv",
              index=False, encoding="utf-8")

    # T2 — morbidade: capítulo CID-10 × mês × sexo
    t2 = (df.groupby(["cap_cid", "cap_cid_desc", "mes", "sexo"], as_index=False)
            .agg(internacoes=("VAL_TOT", "size"),
                 valor_total_brl=("VAL_TOT", "sum"),
                 obitos=("MORTE", "sum")))
    t2["valor_total_brl"] = t2["valor_total_brl"].round(2)
    t2.to_csv(CLEAN / "sih_rj_2025_capitulo_cid_mes.csv", index=False, encoding="utf-8")

    # T3 — resumo mensal estadual
    t3 = (df.groupby("mes", as_index=False)
            .agg(internacoes=("VAL_TOT", "size"),
                 valor_total_brl=("VAL_TOT", "sum"),
                 dias_permanencia=("QT_DIARIAS", "sum"),
                 obitos=("MORTE", "sum")))
    t3["media_permanencia_dias"] = (t3["dias_permanencia"] / t3["internacoes"]).round(2)
    t3["taxa_mortalidade_pct"] = (100 * t3["obitos"] / t3["internacoes"]).round(2)
    t3["valor_total_brl"] = t3["valor_total_brl"].round(2)
    t3.to_csv(CLEAN / "sih_rj_2025_resumo_mensal.csv", index=False, encoding="utf-8")

    print(f"T1 {len(t1):,} linhas · T2 {len(t2):,} · T3 {len(t3)}")
    print("Total 2025:", f"{len(df):,} internações ·",
          f"R$ {df['VAL_TOT'].sum():,.2f} ·", f"{df['MORTE'].sum():,} óbitos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
