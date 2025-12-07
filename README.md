# Quebec Payroll Application

A lightweight, modular payroll calculator for Quebec employees, built with Python.

## Features
*   **Precise Calculations**: Uses `decimal.Decimal` for financial accuracy.
*   **Quebec Compliance**: Includes logic for:
    *   Federal Tax (with Quebec Abatement)
    *   Revenu Québec (Provincial Tax)
    *   QPP (Quebec Pension Plan)
    *   QPIP (Quebec Parental Insurance Plan)
    *   EI (Employment Insurance - Quebec Rate)
*   **Cheque Generation**: Data structure ready for printing, including number-to-words conversion.

## Project Structure
```
src/
  payroll_engine.py  # Core logic
  cheque_model.py    # Cheque data structure
tests/
  test_payroll.py    # Unit tests
```

## Setup & Usage

### Prerequisites
*   Python 3.8+

### Installation
1.  Clone the repository or download the files.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running Tests
To verify the calculations:
```bash
pytest tests/test_payroll.py
```

### Example Usage (Python)
```python
from decimal import Decimal
from src.payroll_engine import QuebecPayrollCalculator

calc = QuebecPayrollCalculator()
stub = calc.calculate_paycheck(Decimal("60000.00"), "bi-weekly")

print(f"Gross: {stub.gross_pay}")
print(f"Net: {stub.net_pay}")
print(f"QC Tax: {stub.qc_tax}")
```
