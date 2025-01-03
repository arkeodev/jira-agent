import mesop as me

# local imports
try:
    from .utils import ui_components
except Exception:
    from utils import ui_components


@me.page(path="/")
def page(security_policy=me.SecurityPolicy(dangerously_disable_trusted_types=True)):
    with me.box(
        style=me.Style(
            background="#fff",
            min_height="calc(100% - 48px)",
            padding=me.Padding(bottom=16),
        )
    ):
        with me.box(
            style=me.Style(
                width="min(800px, 100%)",
                margin=me.Margin.symmetric(horizontal="auto"),
                padding=me.Padding.symmetric(
                    horizontal=16,
                ),
            )
        ):
            ui_components.header_text()
            ui_components.example_row()
            ui_components.chat_input()
            ui_components.output()
            ui_components.clear_output()
    ui_components.footer()


@me.page(path="/error")
def error(security_policy=me.SecurityPolicy(dangerously_disable_trusted_types=True)):
    with me.box(
        style=me.Style(
            background="#fff",
            min_height="calc(100% - 48px)",
            padding=me.Padding(bottom=16),
        )
    ):
        with me.box(
            style=me.Style(
                width="min(720px, 100%)",
                margin=me.Margin.symmetric(horizontal="auto"),
                padding=me.Padding.symmetric(
                    horizontal=16,
                ),
            )
        ):
            ui_components.header_text()
            ui_components.render_error_page()
    ui_components.footer()
