# FRP v3.2.0 Test Report

## Result

`PASS`

## Qualification Scope

| Qualification layer | Result |
|---|---|
| M17 through M29 milestone evidence | `13 / 13 PASS` |
| indexed schemas | `124` |
| indexed canonical artifacts | `109` |
| indexed workflows | `40` |
| qualification manifests | `20 PASS` |
| deterministic M30 generations | `2 / 2 byte-identical` |
| archival package construction | `PASS` |
| archival package verification | `PASS` |
| immutable core validation | `PASS` |
| Observatory boundary validation | `PASS` |
| repository alignment validation | `PASS` |

## Execution Commands

`python -m unittest -v tests.test_frp_m30_reproducibility_qualification_archival_closure`

`python -m unittest discover -s tests -p 'test_*.py' -v`

`python frp_m30_reproducibility_qualification_archival_closure.py --verify --repository-root . --source-commit ff3dd434da5dcbd9e8fa62444f658ed4c495b540`

The GitHub Actions M30 workflow commits this report only after the focused and
complete repository suites pass.
