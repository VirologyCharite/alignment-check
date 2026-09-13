import base64
import io
import re

from PIL import Image

from alignment_check.compare.gap_image_plot import render_gap_image_plot


def _decode_first_image(html: str) -> Image.Image:
    match = re.search(r'src="data:image/png;base64,([^"]+)"', html)
    assert match is not None
    return Image.open(io.BytesIO(base64.b64decode(match.group(1))))


def _image_data(grid: list[list[int]], row_ids: list[str], columns: list[int]) -> dict:
    return {
        "grid": grid,
        "row_ids": row_ids,
        "columns": columns,
        "num_columns_shown": len(columns),
        "num_columns_total": max(columns, default=-1) + 1,
    }


def test_render_gap_image_plot_native_resolution_pixels() -> None:
    image_data = _image_data(
        grid=[[1, 1, 1], [0, 0, 0]], row_ids=["a", "b"], columns=[0, 1, 2]
    )
    html = render_gap_image_plot(image_data, image_data)
    image = _decode_first_image(html).convert("L")

    # No scaling: image dimensions match the grid exactly.
    assert image.size == (3, 2)
    assert image.getpixel((0, 0)) == 0  # black: gap
    assert image.getpixel((0, 1)) == 255  # white: no gap


def test_render_gap_image_plot_embeds_two_png_images() -> None:
    image_a = _image_data([[1, 0], [0, 1]], ["a", "b"], [0, 1])
    image_b = _image_data([[0], [1]], ["a", "b"], [3])
    html = render_gap_image_plot(image_a, image_b, "Alignment A", "Alignment B")

    assert html.count('<img src="data:image/png;base64,') == 2
    assert "Alignment A" in html
    assert "Alignment B" in html
    assert "plotly" not in html.lower()


def test_render_gap_image_plot_no_sequence_names_shown() -> None:
    image_data = _image_data([[1, 0]], ["a_very_specific_sequence_id"], [0, 1])
    html = render_gap_image_plot(image_data, image_data)
    assert "a_very_specific_sequence_id" not in html


def test_render_gap_image_plot_ruler_uses_real_column_numbers() -> None:
    # 20 shown columns, contiguous but starting at real (0-based)
    # position 4, not 0. The ruler must label ticks with the real
    # 1-based position (5, 24), not the shown pixel's 1-based index
    # (1, 20).
    columns = list(range(4, 24))
    grid = [[0] * 20]
    image_data = _image_data(grid, ["a"], columns)
    html = render_gap_image_plot(image_data, image_data)
    assert ">5<" in html
    assert ">24<" in html


def test_render_gap_image_plot_no_ruler_when_columns_are_compressed() -> None:
    # Non-contiguous columns mean the shown positions don't increase
    # evenly, so a ruler would be misleading -- it should be omitted.
    columns = [4 + 5 * i for i in range(20)]
    grid = [[0] * 20]
    image_data = _image_data(grid, ["a"], columns)
    html = render_gap_image_plot(image_data, image_data)
    assert 'class="gap-image-ruler"' not in html
    assert ">20<" not in html


def test_render_gap_image_plot_has_sync_scroll_hooks() -> None:
    image_data = _image_data([[1, 0]], ["a"], [0, 1])
    html = render_gap_image_plot(image_data, image_data)
    assert html.count("data-gap-scroll>") == 2
    assert "querySelectorAll" in html


def test_render_gap_image_plot_divider_line_is_drawn() -> None:
    image_data = _image_data(
        grid=[[0, 0], [0, 0], [1, 1], [1, 1]],
        row_ids=["c1", "c2", "u1", "u2"],
        columns=[0, 1],
    )
    with_divider = render_gap_image_plot(
        image_data, image_data, divider_after_row_a=2, divider_after_row_b=2
    )
    without_divider = render_gap_image_plot(image_data, image_data)

    image_with = _decode_first_image(with_divider).convert("RGB")
    image_without = _decode_first_image(without_divider).convert("RGB")

    assert image_with.height == image_without.height + 1
    column = [image_with.getpixel((0, y)) for y in range(image_with.height)]
    assert (220, 0, 0) in column
    assert "2 common sequences" in with_divider
    assert "unique to this file" in with_divider


def test_render_gap_image_plot_no_divider_by_default() -> None:
    image_data = _image_data([[0, 0], [1, 1]], ["a", "b"], [0, 1])
    html = render_gap_image_plot(image_data, image_data)
    image = _decode_first_image(html).convert("RGB")
    column = [image.getpixel((0, y)) for y in range(image.height)]
    assert (220, 0, 0) not in column
    assert "common sequences" not in html


def test_render_gap_image_plot_divider_at_edge_is_ignored() -> None:
    image_data = _image_data([[0, 0], [1, 1]], ["a", "b"], [0, 1])
    for edge in (0, 2):
        html = render_gap_image_plot(
            image_data, image_data, divider_after_row_a=edge
        )
        image = _decode_first_image(html).convert("RGB")
        column = [image.getpixel((0, y)) for y in range(image.height)]
        assert (220, 0, 0) not in column


def test_render_gap_image_plot_empty_grid_does_not_crash() -> None:
    empty_image = _image_data([], [], [])
    html = render_gap_image_plot(empty_image, empty_image)
    assert html.count("<img") == 2
