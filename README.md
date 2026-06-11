# Internações hospitalares do SUS no Rio de Janeiro — 2025 (SIH/SUS)

Base de dados **aberta e reutilizável** derivada dos microdados públicos do **SIH/SUS** (Sistema de Informações Hospitalares do SUS), produzida no âmbito do **TED 77/2024 — Transformação Digital do SUS** (Ministério da Saúde/SEIDIGI · Universidade Federal Fluminense · FEC).

A base aplica a metodologia descrita no artigo do projeto *Building Health Management Dashboards with DATASUS Public Data* (IEEE INDUSCON): extração programática dos arquivos de disseminação do DATASUS, limpeza e padronização (códigos IBGE de município, especialidade do leito, capítulo CID-10) e organização analítica pronta para painéis de Business Intelligence.

## Conteúdo

| Arquivo | Grão | Linhas |
|---|---|---|
| `clean/sih_rj_2025_municipio_mes_especialidade.csv` | município de residência × mês × especialidade | ~9 mil |
| `clean/sih_rj_2025_capitulo_cid_mes.csv` | capítulo CID-10 × mês × sexo | ~480 |
| `clean/sih_rj_2025_resumo_mensal.csv` | mês (série estadual) | 12 |

**Cobertura:** internações (AIHs aprovadas) processadas no estado do RJ, competências 2025-01 a 2025-12 — **926.136 internações**, **R$ 1,71 bilhão** em valores aprovados.

- Esquema e tipos: [`datapackage.json`](datapackage.json) (padrão [Frictionless Data](https://frictionless.io), validado)
- Dicionário de dados e notas metodológicas: [`docs/dicionario.md`](docs/dicionario.md)
- Pipeline reproduzível (Python): `etl_datasus_sih_rj.py` (neste repositório)

## Painel interativo

Os dados alimentam o painel público em Looker Studio do projeto — link no portal do TED 77/2024.

## Fontes

- DATASUS — arquivos de disseminação SIH/SUS (AIH reduzida, `RDRJ25MM.dbc`): `ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Dados`
- IBGE — API de localidades (nomes de municípios do RJ)

## Licença e citação

Dados derivados de dados públicos do Ministério da Saúde. Esta compilação é distribuída sob **CC-BY 4.0** — cite como:

> TED 77/2024 — Transformação Digital do SUS (UFF/FEC/SEIDIGI-MS). *Internações hospitalares do SUS no Rio de Janeiro — 2025 (SIH/SUS)*, v1.0.0, 2026.

## Avisos de uso

- A unidade de registro é a **AIH aprovada** (aproximação usual de "internação"); reapresentações e AIHs de longa permanência seguem as regras do SIH/SUS.
- O município é o de **residência** do paciente; internações de residentes de outras UFs aparecem como "Outros estados / ignorado".
- Valores em reais correntes, sem deflacionamento.
