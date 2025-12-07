import pytest
from decimal import Decimal
from src.payroll_engine import QuebecPayrollCalculator, TaxConstants
from src.cheque_model import ChequeModel

def test_payroll_calculation_smoke():
    # Smoke test with a standard salary
    # 60k annual, bi-weekly
    calc = QuebecPayrollCalculator()
    salary = Decimal("60000.00")
    stub = calc.calculate_paycheck(salary, "bi-weekly")
    
    assert stub.gross_pay > 0
    assert stub.net_pay < stub.gross_pay
    assert stub.fed_tax > 0
    assert stub.qc_tax > 0
    assert stub.qpp_deduction > 0
    assert stub.ei_deduction > 0
    assert stub.qpip_deduction > 0
    
    # Check basic math integrity
    calculated_net = stub.gross_pay - (stub.fed_tax + stub.qc_tax + stub.qpp_deduction + stub.ei_deduction + stub.qpip_deduction)
    # Allow small rounding diff of 1 cent due to component rounding vs total rounding
    assert abs(calculated_net - stub.net_pay) <= Decimal("0.01")

def test_number_to_words():
    amount = Decimal("1234.56")
    words = ChequeModel.number_to_words(amount)
    assert "One Thousand Two Hundred And Thirty-Four Dollars and 56/100" in words

def test_high_income_brackets():
    # Test high income to ensure max contributions are capped
    calc = QuebecPayrollCalculator()
    salary = Decimal("200000.00") # Well above max pensionable/insurable
    stub = calc.calculate_paycheck(salary, "monthly") # 12 periods
    
    # Check if annualized deductions match max constants (approx)
    # Note: The calculator does annualized estimation / periods.
    
    annual_qpp = stub.qpp_deduction * 12
    # Allow small rounding error margin
    assert abs(annual_qpp - calc.constants.QPP_MAX_CONTRIBUTION) < Decimal("1.00")
    
    annual_ei = stub.ei_deduction * 12
    assert abs(annual_ei - calc.constants.EI_MAX_PREMIUM) < Decimal("1.00")
