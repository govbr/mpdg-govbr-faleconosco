import martian
from grokcore.component.tests.grokker.onlyonce_fixture.component import Alpha

class AlphaGrokker(martian.ClassGrokker):
    martian.component(Alpha)

    def grok(self, name, factory, module_info, **kw):
        print("alpha")
        return True
