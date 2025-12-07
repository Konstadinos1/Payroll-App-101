from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import Dict, Optional

# Constants for 2024 (Example values - normally would be loaded from a config)
# These are approximate for demonstration purposes.
# In a real app, these would be in a database or external JSON configuration.

@dataclass
class TaxConstants:
    YEAR: int = 2024
    
    # Federal
    FED_BASIC_PERSONAL_AMOUNT: Decimal = Decimal("15705.00")
    FED_TAX_BRACKETS: Dict[Decimal, Decimal] = None # Initialized in __post_init__
    
    # Quebec
    QC_BASIC_PERSONAL_AMOUNT: Decimal = Decimal("18056.00")
    QC_TAX_BRACKETS: Dict[Decimal, Decimal] = None # Initialized in __post_init__
    QC_ABATEMENT_RATE: Decimal = Decimal("0.165")
    
    # QPP (Quebec Pension Plan)
    QPP_RATE: Decimal = Decimal("0.0640")
    QPP_MAX_PENSIONABLE_EARNINGS: Decimal = Decimal("68500.00")
    QPP_BASIC_EXEMPTION: Decimal = Decimal("3500.00")
    QPP_MAX_CONTRIBUTION: Decimal = Decimal("4160.00") # Approx
    
    # QPIP (Quebec Parental Insurance Plan)
    QPIP_RATE: Decimal = Decimal("0.00494")
    QPIP_MAX_INSURABLE_EARNINGS: Decimal = Decimal("94000.00")
    QPIP_MAX_PREMIUM: Decimal = Decimal("464.36")
    
    # EI (Employment Insurance) - Quebec Rate
    EI_RATE_QC: Decimal = Decimal("0.0132")
    EI_MAX_INSURABLE_EARNINGS: Decimal = Decimal("63200.00")
    EI_MAX_PREMIUM: Decimal = Decimal("834.24")

    def __post_init__(self):
        # Brackets: {Threshold: Rate}
        # 2024 Federal Brackets
        self.FED_TAX_BRACKETS = {
            Decimal("0.00"): Decimal("0.15"),
            Decimal("55867.00"): Decimal("0.205"),
            Decimal("111733.00"): Decimal("0.26"),
            Decimal("173205.00"): Decimal("0.29"),
            Decimal("246752.00"): Decimal("0.33"),
        }
        
        # 2024 Quebec Brackets
        self.QC_TAX_BRACKETS = {
             Decimal("0.00"): Decimal("0.14"),
             Decimal("51780.00"): Decimal("0.19"),
             Decimal("103545.00"): Decimal("0.24"),
             Decimal("126000.00"): Decimal("0.2575"),
        }

@dataclass
class PayStub:
    gross_pay: Decimal
    net_pay: Decimal
    fed_tax: Decimal
    qc_tax: Decimal
    qpp_deduction: Decimal
    qpip_deduction: Decimal
    ei_deduction: Decimal
    total_deductions: Decimal
    pay_period: str

class QuebecPayrollCalculator:
    def __init__(self, tax_constants: TaxConstants = TaxConstants()):
        self.constants = tax_constants

    def _round_currency(self, amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_tax_from_brackets(self, taxable_income: Decimal, brackets: Dict[Decimal, Decimal]) -> Decimal:
        """Calculates tax based on progressive brackets."""
        tax = Decimal("0.00")
        sorted_brackets = sorted(brackets.items())
        
        previous_threshold = Decimal("0.00")
        previous_rate = Decimal("0.00")
        
        for threshold, rate in sorted_brackets:
            if taxable_income > threshold:
                if previous_threshold == Decimal("0.00") and threshold == Decimal("0.00"):
                     # First bracket logic handling if dict starts at 0
                     previous_rate = rate
                     continue
                
                # Calculate tax for the chunk between previous_threshold and current threshold (or taxable_income)
                # Actually, standard bracket logic:
                # If income is 60k. 
                # 0-55k at 15%
                # 55k-60k at 20.5%
                pass
        
        # Simplified iterative approach
        remaining_income = taxable_income
        calculated_tax = Decimal("0.00")
        
        # We need to iterate through ranges.
        # Create ranges from keys
        thresholds = sorted(brackets.keys())
        rates = [brackets[t] for t in thresholds]
        
        for i in range(len(thresholds)):
            lower = thresholds[i]
            rate = rates[i]
            upper = thresholds[i+1] if i + 1 < len(thresholds) else Decimal("Infinity")
            
            if taxable_income > lower:
                taxable_amount_in_bracket = min(taxable_income, upper) - lower
                calculated_tax += taxable_amount_in_bracket * rate
            else:
                break
                
        return calculated_tax

    def calculate_paycheck(self, annual_gross_salary: Decimal, pay_period: str = "bi-weekly") -> PayStub:
        """
        Calculates a single paycheck based on annual gross salary.
        Note: This is a simplified 'annualized' calculation method.
        Real payroll often calculates based on period income x periods, but for fixed salary this works.
        """
        
        periods_per_year = {
            "weekly": 52,
            "bi-weekly": 26,
            "semi-monthly": 24,
            "monthly": 12
        }.get(pay_period, 26)
        
        gross_pay_per_period = self._round_currency(annual_gross_salary / periods_per_year)
        
        # 1. Calculate QPP
        # Exemption is annual, so we prorate it or use the annual method.
        # Using annual method for simplicity of logic, then dividing by periods for the deduction
        # (In real DAS, you check YTD, but here we assume a stateless calculation for a projection)
        
        qpp_pensionable = min(annual_gross_salary, self.constants.QPP_MAX_PENSIONABLE_EARNINGS) - self.constants.QPP_BASIC_EXEMPTION
        qpp_pensionable = max(qpp_pensionable, Decimal("0.00"))
        annual_qpp = min(qpp_pensionable * self.constants.QPP_RATE, self.constants.QPP_MAX_CONTRIBUTION)
        
        # 2. Calculate QPIP
        qpip_insurable = min(annual_gross_salary, self.constants.QPIP_MAX_INSURABLE_EARNINGS)
        annual_qpip = min(qpip_insurable * self.constants.QPIP_RATE, self.constants.QPIP_MAX_PREMIUM)
        
        # 3. Calculate EI
        ei_insurable = min(annual_gross_salary, self.constants.EI_MAX_INSURABLE_EARNINGS)
        annual_ei = min(ei_insurable * self.constants.EI_RATE_QC, self.constants.EI_MAX_PREMIUM)
        
        # 4. Federal Tax
        # Taxable Income = Gross - Deductions (QPP, QPIP, Union dues etc.)
        # Note: Enhanced QPP is deductible, base is a credit. For simplicity here, we treat standard deductions.
        # We will use the simplified "Gross - Basic Exemption" for quick estimation or full bracket calc.
        # Let's use full bracket calc on (Gross - Deductions)
        
        # Federal Taxable Income
        # Deduction for QPP/QPIP enhanced portions is complex. 
        # Simplified: Taxable Income = Gross - (Union Dues, RPP, etc). 
        # Credits are applied AFTER tax calculation (Basic Personal Amount, CPP/EI credits).
        
        fed_taxable_income = annual_gross_salary 
        gross_fed_tax = self.calculate_tax_from_brackets(fed_taxable_income, self.constants.FED_TAX_BRACKETS)
        
        # Federal Non-Refundable Tax Credits
        # 1. Basic Personal Amount
        # 2. CPP/QPP contributions (Base)
        # 3. EI premiums
        # 4. Canada Employment Amount (approx 1368 for 2024)
        
        fed_credits_base = self.constants.FED_BASIC_PERSONAL_AMOUNT + annual_qpp + annual_ei + annual_qpip + Decimal("1368.00") 
        fed_credits_value = fed_credits_base * Decimal("0.15") # Lowest bracket rate
        
        net_fed_tax = max(gross_fed_tax - fed_credits_value, Decimal("0.00"))
        
        # Quebec Abatement (16.5% of Basic Federal Tax)
        # Applied to residents of Quebec
        abatement = net_fed_tax * self.constants.QC_ABATEMENT_RATE
        final_fed_tax = max(net_fed_tax - abatement, Decimal("0.00"))
        
        # 5. Quebec Provincial Tax
        qc_taxable_income = annual_gross_salary
        gross_qc_tax = self.calculate_tax_from_brackets(qc_taxable_income, self.constants.QC_TAX_BRACKETS)
        
        # Quebec Non-Refundable Tax Credits
        # 1. Basic Personal Amount
        # 2. QPP/QPIP/EI
        qc_credits_base = self.constants.QC_BASIC_PERSONAL_AMOUNT + annual_qpp + annual_ei + annual_qpip
        qc_credits_value = qc_credits_base * Decimal("0.14") # Lowest QC bracket
        
        final_qc_tax = max(gross_qc_tax - qc_credits_value, Decimal("0.00"))
        
        # Convert Annual to Period
        period_qpp = self._round_currency(annual_qpp / periods_per_year)
        period_qpip = self._round_currency(annual_qpip / periods_per_year)
        period_ei = self._round_currency(annual_ei / periods_per_year)
        period_fed_tax = self._round_currency(final_fed_tax / periods_per_year)
        period_qc_tax = self._round_currency(final_qc_tax / periods_per_year)
        
        total_deductions = period_qpp + period_qpip + period_ei + period_fed_tax + period_qc_tax
        net_pay = gross_pay_per_period - total_deductions
        
        return PayStub(
            gross_pay=gross_pay_per_period,
            net_pay=net_pay,
            fed_tax=period_fed_tax,
            qc_tax=period_qc_tax,
            qpp_deduction=period_qpp,
            qpip_deduction=period_qpip,
            ei_deduction=period_ei,
            total_deductions=total_deductions,
            pay_period=pay_period
        )
