import pytest
from densitree.steps.base import BaseStep


def test_base_step_is_abstract():
    with pytest.raises(TypeError):
        BaseStep()


def test_concrete_step_must_implement_run():
    class Incomplete(BaseStep):
        pass
    with pytest.raises(TypeError):
        Incomplete()


def test_concrete_step_run_returns_dict():
    class MyStep(BaseStep):
        def run(self, data, **ctx):
            return {"result": 42}

    step = MyStep()
    out = step.run(None)
    assert out == {"result": 42}
