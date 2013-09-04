import gamelib.model

def test_recorder(monkeypatch):
    class Game:
        turn = 10
    monkeypatch.setattr(gamelib.model, 'game', Game)

    class T(object):
        a = gamelib.model.RecordedAttribute('a')

    t = T()
    assert t.a is None
    t.a = 'one'

    assert t.a == 'one'
    assert t.a_value == 'one'
    assert t.a_history == [(10, 'one')]

    Game.turn = 11
    t.a = 'two'
    assert t.a_history == [(10, 'one'), (11, 'two')]
    assert t.a == 'two'
