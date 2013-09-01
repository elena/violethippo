from gamelib import plans

def test_plan_registry():
    print plans.registry
    assert any(plan for plan in plans.registry
        if plan.__name__ == 'Noop')
