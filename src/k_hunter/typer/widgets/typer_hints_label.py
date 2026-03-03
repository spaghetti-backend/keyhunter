from textual.reactive import reactive
from textual.widgets import Label


class TyperHints(Label):
    is_active_session: reactive[bool] = reactive(bool, init=False)

    def on_mount(self) -> None:
        self._animation_timer = self.set_interval(1.0, self.animate_label)

    def animate_label(self) -> None:
        target_opacity = 1.0 if self.styles.opacity < 1.0 else 0.5

        self.styles.animate(
            "opacity", value=target_opacity, duration=0.9, easing="linear"
        )

    async def watch_is_active_session(self) -> None:
        if self.is_active_session:
            self.update("'Esc' to cancel")
            self._animation_timer.pause()
            self.app.animator.force_stop_animation(self.styles, "opacity")
            self.styles.opacity = 1.0
        else:
            self.update("Press 'space' to start typing")
            self._animation_timer.resume()
