"""Renders the two alignments' gap-position grids (see `gap_image.py`) as
black-and-white bitmap images, each with a scrollable, ruler-labeled
x-axis showing real alignment column numbers.

A `plotly.graph_objects.Heatmap` was tried here first, but heatmaps
interpolate/smooth between cells by default; with hundreds of thin rows
and a data resolution much higher than the on-screen canvas, that turns
a sharp black/white pattern into misleading colored banding. Building an
actual bitmap, one pixel per site/sequence with no interpolation or
scaling, avoids that entirely: images are embedded at native resolution
and left to scroll rather than shrink, so nothing gets blurred or
invented. The two images' horizontal scroll positions are kept in sync
(via the script at the end of `render_gap_image_plot`'s output) so
scrolling one scrolls the other the same amount.

The ruler above each image labels ticks with the *real* 1-based
alignment column number behind each shown pixel, via `columns` in the
`gap_image.compute_gap_image_rows` data -- this stays correct even when
columns have been compressed (ungapped ones skipped), where pixel
position and real column number diverge.
"""

import base64
import html
import io

from PIL import Image, ImageDraw

_DIVIDER_COLOR = (220, 0, 0)

_RULER_HEIGHT = 14
_RULER_MIN_TICK_SPACING_PX = 40
_NICE_TICK_STEPS = [
    1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500,
    1000, 2000, 2500, 5000, 10000, 20000, 25000, 50000, 100000,
]

_STYLE = """
.gap-image-legend { font-size: 0.85rem; color: #444; margin-bottom: 0.75rem; }
.gap-image-legend .swatch { display: inline-block; width: 0.9em; height: 0.9em;
    vertical-align: -0.1em; border: 1px solid #999; margin-right: 0.3em; }
.gap-image-caption { font-size: 0.9rem; color: #444; margin: 0 0 0.5rem 0; }
.gap-image-wrap { overflow: auto; border: 1px solid #ccc; max-width: 100%;
    margin-bottom: 2rem; }
.gap-image-wrap img { display: block; image-rendering: pixelated;
    image-rendering: crisp-edges; }
.gap-image-ruler { position: sticky; top: 0; background: #fff; z-index: 1;
    border-bottom: 1px solid #ddd; }
.gap-image-ruler svg { display: block; }
"""

_SYNC_SCROLL_SCRIPT = """
(function() {
  var wraps = Array.prototype.slice.call(
    document.querySelectorAll('[data-gap-scroll]')
  );
  var syncing = null;
  wraps.forEach(function(el) {
    el.addEventListener('scroll', function() {
      if (syncing && syncing !== el) return;
      syncing = el;
      wraps.forEach(function(other) {
        if (other !== el) other.scrollLeft = el.scrollLeft;
      });
      syncing = null;
    });
  });
})();
"""


def _is_contiguous(columns: list[int]) -> bool:
    """Whether `columns` is a run of consecutive integers.

    True for the uncompressed case (every column shown, so position
    increases evenly and a ruler is meaningful). False once columns have
    been compressed out, since the gaps between shown columns then vary
    and a ruler's evenly-spaced ticks would misleadingly suggest an even
    spacing that isn't really there.
    """
    return columns == list(range(columns[0], columns[0] + len(columns)))


def _build_ruler(columns: list[int]) -> str:
    """An SVG ruler labeling each shown column with its real, 1-based
    alignment column number. Exactly `len(columns)` px wide, so it lines
    up with the gap image below it (1 image pixel = 1 shown column).

    Returns "" if `columns` is empty or not contiguous (see
    `_is_contiguous`) -- a ruler isn't meaningful once the shown
    columns' real positions no longer increase evenly.
    """
    width = len(columns)
    if width <= 0 or not _is_contiguous(columns):
        return ""

    step = next(
        (n for n in _NICE_TICK_STEPS if n >= _RULER_MIN_TICK_SPACING_PX),
        _NICE_TICK_STEPS[-1],
    )

    last_index = width - 1
    tick_positions = list(range(0, width, step))
    if not tick_positions or (last_index - tick_positions[-1]) >= step / 3:
        tick_positions.append(last_index)

    parts = [
        f'<svg width="{width}" height="{_RULER_HEIGHT}" '
        f'viewBox="0 0 {width} {_RULER_HEIGHT}" xmlns="http://www.w3.org/2000/svg">'
    ]
    for x in tick_positions:
        label = columns[x] + 1  # 1-based real alignment column number
        if x <= 3:
            anchor = "start"
        elif x >= width - 4:
            anchor = "end"
        else:
            anchor = "middle"
        parts.append(
            f'<line x1="{x}" y1="9" x2="{x}" y2="{_RULER_HEIGHT}" stroke="#999"/>'
        )
        parts.append(
            f'<text x="{x}" y="7" font-size="8" '
            'font-family="ui-monospace, Menlo, Consolas, monospace" '
            f'text-anchor="{anchor}" fill="#555">{label}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def _grid_to_image(
    grid: list[list[int]], divider_after_row: int | None = None
) -> Image.Image:
    """Render a 0/1 grid as a black (1)-on-white (0) image, at native
    resolution (one pixel per site/sequence, no scaling).

    Args:
        grid: One row per sequence, one column per shown site.
        divider_after_row: If given (and strictly between 0 and the
            number of rows), a 1-pixel-tall red line is inserted after
            this many rows, to separate common sequences (above) from
            sequences unique to this file (below).

    Returns:
        An RGB image.
    """
    num_rows = len(grid)
    num_columns = len(grid[0]) if num_rows else 0
    if num_rows == 0 or num_columns == 0:
        return Image.new("RGB", (1, 1), color=(255, 255, 255))

    row_bytes = (bytes(0 if value else 255 for value in row) for row in grid)
    gray = Image.frombytes("L", (num_columns, num_rows), b"".join(row_bytes))
    image = gray.convert("RGB")

    if divider_after_row is None or not (0 < divider_after_row < num_rows):
        return image

    width, height = image.size
    combined = Image.new("RGB", (width, height + 1))
    combined.paste(image.crop((0, 0, width, divider_after_row)), (0, 0))
    combined.paste(
        image.crop((0, divider_after_row, width, height)),
        (0, divider_after_row + 1),
    )
    ImageDraw.Draw(combined).line(
        [(0, divider_after_row), (width - 1, divider_after_row)],
        fill=_DIVIDER_COLOR,
    )
    return combined


def _image_to_data_uri(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _render_one(
    image_data: dict[str, object], title: str, divider_after_row: int | None
) -> str:
    image = _grid_to_image(image_data["grid"], divider_after_row)
    data_uri = _image_to_data_uri(image)
    ruler = _build_ruler(image_data["columns"])

    num_rows = len(image_data["row_ids"])
    if divider_after_row is None:
        row_summary = f"{num_rows} sequences"
    else:
        num_unique = num_rows - divider_after_row
        row_summary = (
            f"{divider_after_row} common sequences, {num_unique} unique to "
            "this file below the red line"
        )
    caption = (
        f"{html.escape(title)}: {image_data['num_columns_shown']} of "
        f"{image_data['num_columns_total']} columns shown, {row_summary}"
    )
    ruler_html = f'<div class="gap-image-ruler">{ruler}</div>' if ruler else ""
    return (
        f'<p class="gap-image-caption">{caption}</p>'
        '<div class="gap-image-wrap" data-gap-scroll>'
        f"{ruler_html}"
        f'<img src="{data_uri}" width="{image.width}" height="{image.height}" '
        f'alt="{html.escape(title)} gap positions">'
        "</div>"
    )


def render_gap_image_plot(
    image_a: dict[str, object],
    image_b: dict[str, object],
    title_a: str = "Alignment A",
    title_b: str = "Alignment B",
    divider_after_row_a: int | None = None,
    divider_after_row_b: int | None = None,
) -> str:
    """Render two gap-position grids as stacked, ruler-labeled images.

    Sequences are not labeled on the images (there usually isn't room);
    the common-sequence rows use the same order in both images, so a
    given row index refers to the same sequence in each, up to
    `divider_after_row_*`. Images are embedded at native resolution and
    scroll rather than shrink; the two images' horizontal scroll
    positions are kept in sync with each other.

    Args:
        image_a: The return value of `gap_image.compute_gap_image_rows`
            for the first alignment; its rows should be the common
            sequences followed by any sequences unique to A.
        image_b: Same, for the second alignment (common sequences,
            in the same order as `image_a`, followed by any unique to B).
        title_a: Caption title for the first image.
        title_b: Caption title for the second image.
        divider_after_row_a: Row index (0-based count) after which to
            draw the red divider in image A, or None for no divider.
        divider_after_row_b: Same, for image B.

    Returns:
        An HTML fragment holding both images, stacked vertically.
    """
    legend = (
        '<div class="gap-image-legend">'
        '<span class="swatch" style="background:#000;"></span>gap &nbsp;'
        '<span class="swatch" style="background:#fff;"></span>not a gap &nbsp;'
        '<span class="swatch" style="background:rgb(220,0,0);"></span>'
        "divider between common and file-specific rows</div>"
    )
    return (
        f"<style>{_STYLE}</style>"
        f"{legend}"
        f"{_render_one(image_a, title_a, divider_after_row_a)}"
        f"{_render_one(image_b, title_b, divider_after_row_b)}"
        f"<script>{_SYNC_SCROLL_SCRIPT}</script>"
    )
