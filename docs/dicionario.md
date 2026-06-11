# Dicionário de dados — DS-01 · SIH/SUS RJ 2025


## `sih_rj_2025_municipio_mes_especialidade.csv`

Internações por município de residência, mês e especialidade.

| Campo | Tipo | Descrição |
|---|---|---|
| `cod_mun` | string | Código IBGE do município de residência (6 dígitos) |
| `municipio` | string | Nome do município de residência (RJ) ou 'Outros estados / ignorado' |
| `mes` | string | Competência no formato AAAA-MM |
| `especialidade` | string | Especialidade do leito (tabela ESPEC do SIH/SUS) |
| `internacoes` | integer | Número de internações (AIHs aprovadas) no grupo |
| `valor_total_brl` | number | Valor total das AIHs em reais (R$) |
| `dias_permanencia` | integer | Soma dos dias de permanência (QT_DIARIAS) |
| `obitos` | integer | Internações com desfecho óbito (MORTE=1) |

## `sih_rj_2025_capitulo_cid_mes.csv`

Internações por capítulo CID-10, mês e sexo.

| Campo | Tipo | Descrição |
|---|---|---|
| `cap_cid` | string | Capítulo CID-10 (I a XXII; ND = não informado) |
| `cap_cid_desc` | string | Descrição curta do capítulo CID-10 |
| `mes` | string | Competência no formato AAAA-MM |
| `sexo` | string | Sexo do paciente (Masculino/Feminino/Não informado) |
| `internacoes` | integer | Número de internações (AIHs aprovadas) no grupo |
| `valor_total_brl` | number | Valor total das AIHs em reais (R$) |
| `obitos` | integer | Internações com desfecho óbito (MORTE=1) |

## `sih_rj_2025_resumo_mensal.csv`

Resumo mensal estadual (RJ).

| Campo | Tipo | Descrição |
|---|---|---|
| `mes` | string | Competência no formato AAAA-MM |
| `internacoes` | integer | Número de internações (AIHs aprovadas) no grupo |
| `valor_total_brl` | number | Valor total das AIHs em reais (R$) |
| `dias_permanencia` | integer | Soma dos dias de permanência (QT_DIARIAS) |
| `obitos` | integer | Internações com desfecho óbito (MORTE=1) |
| `media_permanencia_dias` | number | Dias de permanência / internações |
| `taxa_mortalidade_pct` | number | 100 × óbitos / internações |


## Notas metodológicas
- Unidade de registro da fonte: AIH (Autorização de Internação Hospitalar) aprovada — aproximação usual de 'internação' no SIH/SUS.
- Competências 2025-01 a 2025-12; UF de internação: RJ; município refere-se à RESIDÊNCIA do paciente (MUNIC_RES), podendo incluir residentes de outras UFs.
- Capítulo CID-10 derivado do diagnóstico principal (DIAG_PRINC).
- Valores em R$ correntes, sem deflacionamento.
- Pipeline reproduzível: `scripts/dados/etl_datasus_sih_rj.py` no repositório do projeto.
