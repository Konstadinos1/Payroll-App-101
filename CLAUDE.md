# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Quebec payroll calculator in pure Python (no framework, no database). It computes per-period paycheck deductions for Quebec employees — federal tax (with the Quebec abatement), Revenu Québec provincial tax, QPP, QPIP, and EI at the Quebec rate — and produces cheque-ready data. This is Quebec-specific payroll: QPP and QPIP apply, **not** CPP and standard EI.

## Commands

```bash
pip install -r requirements.txt   # deps: pytest, pydantic, inflect

python -m pytest                  # run all tests
python -m pytest tests/test_payroll.py::test_high_income_brackets   # run a single test
```

Run tests from the repo root with `python -m pytest` (not bare `pytest`): tests import `src.payroll_engine`, and only the `-m` form puts the repo root on `sys.path` — there is no conftest.py or packaging config to do it otherwise.

## Architecture

Two source modules under `src/`, connected by the `PayStub` dataclass:

- **`src/payroll_engine.py`** — core calculation logic.
  - `TaxConstants`: dataclass holding all 2024 rates, brackets, maximums, and exemptions (federal/QC brackets are built in `__post_init__`). These are hardcoded example values; the stated intent is to eventually load them from external config. When rates change, this is the only place to edit.
  - `QuebecPayrollCalculator.calculate_paycheck()`: the main entry point. It uses a **stateless annualized method** — computes annual deductions from annual gross salary, caps them at annual maximums (QPP/QPIP/EI), then divides by pay periods (weekly/bi-weekly/semi-monthly/monthly). It does not track year-to-date amounts like real DAS remittance would; it is a projection, and tests are written to that assumption.
  - Tax credit handling: gross tax from progressive brackets, then non-refundable credits (basic personal amount + QPP/QPIP/EI contributions) valued at the lowest bracket rate (15% federal, 14% QC), then the 16.5% Quebec abatement on net federal tax.
  - `PayStub`: the output dataclass consumed by the cheque model.
- **`src/cheque_model.py`** — `ChequeModel` (Pydantic) turns a `PayStub` into printable cheque data via `from_paystub()`, including English number-to-words conversion using `inflect`.

## Conventions

- **All money is `decimal.Decimal`** — never float. Currency rounding goes through `_round_currency()` (`ROUND_HALF_UP` to 2 places). Tests tolerate ≤ $0.01 drift between component rounding and totals.
- Payroll logic must follow Revenu Québec (RQ) and CRA rules; test names spell out the Quebec-specific behavior being verified (e.g. contribution caps at max pensionable/insurable earnings).
- Every change to calculation logic needs tests, including boundary cases (income above QPP/QPIP/EI maximums, bracket thresholds).
- Type hints on everything; Pydantic for validation of external-facing models.
- Dates: ISO 8601 internally; display as DD/MM/YYYY (Quebec convention). User-facing strings in French for Quebec-market apps; code and comments in English.
- Git: branch naming `feat/…`, `fix/…`, `chore/…`, `refactor/…`; conventional commit messages; never push directly to `main` — always PR.

See `AGENTS.md` for the developer's general cross-repo agent instructions.
