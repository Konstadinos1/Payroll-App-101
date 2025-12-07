from pydantic import BaseModel
from decimal import Decimal
from datetime import date
import inflect

class ChequeModel(BaseModel):
    payee_name: str
    payment_date: date
    amount_numeric: Decimal
    amount_words: str
    memo: str = "Payroll"
    
    @staticmethod
    def number_to_words(amount: Decimal) -> str:
        p = inflect.engine()
        dollars = int(amount)
        cents = int((amount - dollars) * 100)
        
        words = p.number_to_words(dollars).replace(",", "")
        words = words.title()
        
        return f"{words} Dollars and {cents:02d}/100"

    @classmethod
    def from_paystub(cls, payee_name: str, paystub, payment_date: date = date.today()):
        return cls(
            payee_name=payee_name,
            payment_date=payment_date,
            amount_numeric=paystub.net_pay,
            amount_words=cls.number_to_words(paystub.net_pay),
            memo=f"Salary - {paystub.pay_period}"
        )
