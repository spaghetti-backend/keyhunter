import random

from .typer import Typer


class TyperSimulator(Typer, can_focus=False):
    def on_mount(self) -> None:
        super().on_mount()
        self._simulate_timer = self.set_interval(
            0.2, self._simulate_key_press, pause=True
        )

    def simulate(self) -> None:
        self._test_content = self.app.content_service.generate()
        self._test_content_idx = 0
        self.engine.prepare_content(self._test_content)
        self._is_active_session = True

    def resume(self) -> None:
        self._simulate_timer.resume()

    def pause(self) -> None:
        self._simulate_timer.pause()

    def _simulate_key_press(self):
        if random.random() < 0.9:
            self.engine.mark_current_char(True)
        else:
            self.engine.mark_current_char(False)

        if self.engine.has_next:
            self.engine.next()
        else:
            self.pause()
            self.simulate()
            self.resume()
        self.refresh()

    def _on_engine_changed(self) -> None:
        self.pause()
        super()._on_engine_changed()
        self.simulate()
        self.resume()
