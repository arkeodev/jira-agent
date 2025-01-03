import mesop as me

# local imports
from . import api_utils, config


def header_text():
    with me.box(
        style=me.Style(
            padding=me.Padding(
                top=50,
                bottom=10,
            ),
        )
    ):
        me.icon(
            "psychology",
            style=me.Style(
                display="block",
                width="100%",
                height="100%",
                font_size=50,
                text_align="center",
                font_weight=100,
                background="linear-gradient(90deg, #4285F4, #AA5CDB, #DB4437) text",
                color="transparent",
            ),
        )
    with me.box(
        style=me.Style(
            padding=me.Padding(
                top=0,
                bottom=40,
            ),
        )
    ):
        (
            me.text(
                "AI JIRA ASSISTANT ",
                style=me.Style(
                    text_align="center",
                    font_size=30,
                    font_weight=700,
                    background="linear-gradient(90deg, #4285F4, #AA5CDB, #DB4437) text",
                    color="transparent",
                ),
            ),
        )


def clear_output():
    with me.box(style=me.Style(margin=me.Margin.all(15))):
        with me.box(style=me.Style(display="flex", flex_direction="row", gap=12)):
            me.button("Clear output", type="flat", on_click=delete_state_helper)


def delete_state_helper(ClickEvent):
    config.State.output = ""


def example_row():
    is_mobile = me.viewport_size().width < 640
    with me.box(
        style=me.Style(
            display="flex",
            flex_direction="column" if is_mobile else "row",
            gap=10,
            margin=me.Margin(bottom=40),
        )
    ):
        for example in config.EXAMPLE_PROMPTS:
            prompt_box(example, is_mobile)


def prompt_box(example: str, is_mobile: bool):
    with me.box(
        style=me.Style(
            width="100%" if is_mobile else 200,
            height=250,
            text_align="center",
            background="#F0F4F9",
            padding=me.Padding.all(16),
            font_weight=500,
            line_height="1.5",
            border_radius=16,
            cursor="pointer",
        ),
        key=example,
        on_click=click_prompt_box,
    ):
        me.text(example)


def click_prompt_box(e: me.ClickEvent):
    config.State.input = e.key


def chat_input():
    with me.box(
        style=me.Style(
            padding=me.Padding.all(8),
            background="white",
            display="flex",
            width="100%",
            border=me.Border.all(me.BorderSide(width=0, style="solid", color="black")),
            border_radius=12,
            box_shadow="0 10px 20px #0000000a, 0 2px 6px #0000000a, 0 0 1px #0000000a",
        )
    ):
        with me.box(
            style=me.Style(
                flex_grow=1,
            )
        ):
            me.native_textarea(
                value=config.State.input,
                autosize=True,
                min_rows=4,
                placeholder="Enter your prompt",
                style=me.Style(
                    padding=me.Padding(top=16, left=16),
                    background="white",
                    outline="none",
                    width="100%",
                    overflow_y="auto",
                    border=me.Border.all(
                        me.BorderSide(style="none"),
                    ),
                ),
                on_blur=textarea_on_blur,
            )
        with me.content_button(type="icon", on_click=click_send):
            me.icon("send")


def click_send(e: me.ClickEvent):
    if not config.State.input:
        return
    config.State.in_progress = True
    input = config.State.input
    config.State.input = ""
    yield

    try:
        if result := api_utils.call_jira_agent(input):
            config.State.output += result
        else:
            config.State.output += (
                f"Request: {input}<br>Error: Failed to get response from agent<br><br>"
            )
    except Exception as e:
        config.State.output += f"Request: {input}<br>Error: {str(e)}<br><br>"

    config.State.in_progress = False
    yield


def textarea_on_blur(e: me.InputBlurEvent):
    config.State.input = e.value


def output():
    if config.State.output or config.State.in_progress:
        with me.box(
            style=me.Style(
                background="#F0F4F9",
                padding=me.Padding.all(16),
                border_radius=16,
                margin=me.Margin(top=36),
            )
        ):
            if config.State.output:
                me.markdown(config.State.output)
            if config.State.in_progress:
                with me.box(style=me.Style(margin=me.Margin(top=16))):
                    me.progress_spinner()


def footer():
    with me.box(
        style=me.Style(
            position="sticky",
            bottom=0,
            padding=me.Padding.symmetric(vertical=16, horizontal=16),
            width="100%",
            background="#F0F4F9",
            font_size=14,
        )
    ):
        me.html(
            "Made with <a href='https://google.github.io/mesop/'>Mesop</a>",
        )


def navigate_home(event: me.ClickEvent):
    me.navigate("/")


def render_error_page():
    is_mobile = me.viewport_size().width < 640
    with me.box(
        style=me.Style(
            position="sticky",
            width="100%",
            display="block",
            height="100%",
            font_size=50,
            text_align="center",
            flex_direction="column" if is_mobile else "row",
            gap=10,
            margin=me.Margin(bottom=30),
        )
    ):
        me.text(
            "AN ERROR HAS OCCURRED",
            style=me.Style(
                text_align="center",
                font_size=30,
                font_weight=700,
                padding=me.Padding.all(8),
                background="white",
                justify_content="center",
                display="flex",
                width="100%",
            ),
        )
        me.button("Navigate to home page", type="flat", on_click=navigate_home)


if __name__ == "__main__":
    pass
