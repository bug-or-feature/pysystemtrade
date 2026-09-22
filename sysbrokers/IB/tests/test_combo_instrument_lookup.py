from types import SimpleNamespace

from sysbrokers.IB.ib_orders import contract_for_instrument_lookup


def test_combo_uses_first_leg():
    leg = SimpleNamespace(secType="FUT", symbol="M1MS", conId=655438056)
    combo = SimpleNamespace(
        ibcontract=SimpleNamespace(secType="BAG", symbol="M1MS"), legs=[leg]
    )
    assert contract_for_instrument_lookup(combo) is leg


def test_outright_contract_is_used_directly():
    fut = SimpleNamespace(secType="FUT", symbol="FESB")
    assert (
        contract_for_instrument_lookup(SimpleNamespace(ibcontract=fut, legs=[])) is fut
    )


def test_combo_without_resolved_legs_falls_back_to_itself():
    bag = SimpleNamespace(secType="BAG", symbol="M1MS")
    assert (
        contract_for_instrument_lookup(SimpleNamespace(ibcontract=bag, legs=None))
        is bag
    )
