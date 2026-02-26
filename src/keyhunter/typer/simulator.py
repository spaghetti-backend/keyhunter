import random

from keyhunter.typer.widgets import Typer


class TyperSimulator(Typer, can_focus=False):
    def simulate(self, pause: bool = True):
        self._test_content = self.app.content_service.generate()
        self._test_content_idx = 0
        self.engine.prepare_content(self._test_content)
        self._simulate_timer = self.set_interval(0.15, self._simulate_key, pause=pause)
        self._is_active_session = True

    def resume(self):
        self._simulate_timer.resume()

    def pause(self):
        self._simulate_timer.pause()

    def stop(self):
        self._simulate_timer.stop()

    def _simulate_key(self):
        if random.random() < 0.9:
            self.engine.mark_current_char(True)
        else:
            self.engine.mark_current_char(False)

        if self.engine.has_next:
            self.engine.next()
        else:
            self._simulate_timer.stop()
            self.simulate(pause=False)
        self.refresh()

    def _on_engine_changed(self) -> None:
        self.stop()
        super()._on_engine_changed()
        self.simulate(pause=False)
