"""Create an HTML from a Camp object"""

from copy import copy
from functools import partial
from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

from colorcamp.static.html_templates import (
    COLOR_OBJECT_HTML,
    REPORT_TEMPLATE,
    SECTION_HTML,
    SPACE_HTML,
    VALUE_HTML,
)

from ._camp import Bucket, Camp
from .color_space import RGB, BaseColor
from .common.types import ColorSpace
from .common.validators import PathValidator
from .groups import Map, Palette, Scale

__all__ = ["report"]


def _search_buckets(sections: List[str], camp: Camp):
    for section in sections:
        bucket: Bucket = getattr(camp, section)
        if len(bucket.names) > 0:
            yield section, bucket.to_dict()


def _format_header(name: str, color_object) -> str:
    description = "" if color_object.description is None else f"<p>{color_object.description}</p>"
    header = f"<h4>{name}</h4>"

    return f'<div class="tooltip">{header}<span class="tooltiptext">{description}</span></div>'


def _format_color_bar(color_object) -> str:
    color_bar_template = '<div class="color" style="{color_style}">&nbsp;</div>'
    if isinstance(color_object, BaseColor):
        style = f"background-color:{color_object.hex}"
        color_bar = color_bar_template.format(color_style=style)

    elif isinstance(color_object, Palette):
        n_colors = len(color_object)
        stops = [idx / n_colors for idx in range(n_colors + 1)]

        grad = ", ".join(
            [
                f"{color.hex} {stop:.0%}, {color.hex} {stops[idx+1]:.0%}"
                for idx, (color, stop) in enumerate(zip(color_object, stops))
            ]
        )
        style = f"background-image: linear-gradient(to right, {grad})"
        color_bar = color_bar_template.format(color_style=style)

    elif isinstance(color_object, Scale):
        grad = ", ".join([f"{color.hex} {stop:.0%}" for color, stop in zip(color_object, color_object.stops)])
        style = f"background-image: linear-gradient(to right, {grad})"
        color_bar = color_bar_template.format(color_style=style)
    elif isinstance(color_object, Map):
        color_bar = ""

    return color_bar


def _value_formatter(value: Any) -> str:
    if isinstance(value, tuple):
        return "\n".join(
            [VALUE_HTML.format(value=int(val) if isinstance(value, RGB) else f"{val:.2f}") for val in value]
        )
    # if isinstance(value, float):
    #     return VALUE_HTML.format(value=f"{value:.2%}")

    return VALUE_HTML.format(value=value)


def _format_color_spaces_table(color: BaseColor, color_spaces) -> str:
    spaces = ""
    for color_space in color_spaces:
        spaces += SPACE_HTML.format(name=color_space, values=_value_formatter(color.to_color_space(color_space)))

    return spaces


def _format_palette_table(palette: Palette):
    spaces = ""
    for color in palette:
        name = "" if color.name is None else color.name
        values = "\n".join(
            [
                VALUE_HTML.format(value=color.hex),
                VALUE_HTML.format(value=name),
            ]
        )
        spaces += SPACE_HTML.format(name=_format_color_bar(color), values=values)

    return spaces


def _format_scale_table(scale: Scale):
    spaces = ""
    for color, stop in zip(scale.colors, scale.stops):
        name = "" if color.name is None else color.name
        values = "\n".join(
            [
                VALUE_HTML.format(value=color.hex),
                VALUE_HTML.format(value=f"{stop:.2%}"),
                VALUE_HTML.format(value=name),
            ]
        )
        spaces += SPACE_HTML.format(name=_format_color_bar(color), values=values)

    return spaces


def _format_map_table(cmap: Map):
    spaces = ""
    for key, color in cmap.items():
        values = "\n".join(
            [
                VALUE_HTML.format(value=_format_color_bar(color)),
                VALUE_HTML.format(value=color.hex),
            ]
        )
        spaces += SPACE_HTML.format(name=key, values=values)

    return spaces


def camp_to_html(
    camp: Camp,
    color_spaces: Optional[List[ColorSpace]] = None,
    sections: Optional[List[str]] = None,
) -> str:
    """Generate an HTML report of all your colors and color groups that can be easily shipped or shared with any analysis

    Parameters
    ----------
    camp : Camp
        A Camp object to generate the report from
    color_spaces : Optional[List[ColorSpace]], optional
        Order or omit which color spaces are displayed (color section only), by default None
    sections : Optional[List[str]], optional
        Order or omit which sections are displayed. If none are supplied all will be used in order ('colors', 'palettes', 'scales', 'maps'), by default None

    Returns
    -------
    str
        HTML string containing camp report document
    """

    valid_sections = ("colors", "palettes", "scales", "maps")
    valid_color_spaces = tuple(ColorSpace.__args__[1:])  # type: ignore

    css_path = Path(__file__).parent / "static" / "report.css"
    with open(css_path, "r", encoding="UTF-8") as file:
        css = file.read()

    description = "" if camp.description is None else camp.description

    if sections is None:
        sections = copy(valid_sections)  # type: ignore
    else:
        if any((sec not in valid_sections for sec in sections)):
            raise ValueError(f"sections must be one of: {valid_sections}")

    if color_spaces is None:
        color_spaces = valid_color_spaces
    else:
        if any((space not in valid_color_spaces for space in color_spaces)):
            raise ValueError(f"color space must be one of: {valid_color_spaces}")

    table_formatters = {
        "colors": partial(_format_color_spaces_table, color_spaces=color_spaces),
        "palettes": _format_palette_table,
        "scales": _format_scale_table,
        "maps": _format_map_table,
    }

    section_html = ""
    for sec_name, section in _search_buckets(sections, camp):
        content = "".join(
            [
                COLOR_OBJECT_HTML.format(
                    header=_format_header(name, color),
                    color_bar=_format_color_bar(color),
                    spaces=table_formatters[sec_name](color),  # type: ignore
                )
                for name, color in section.items()
            ]
        )

        section_html += SECTION_HTML.format(section_name=sec_name.title(), content=content)

    html_report = REPORT_TEMPLATE.format(
        css=css,
        camp_name=camp.name,
        description=description,
        sections_html=section_html,
    )

    return html_report


def report(
    camp: Camp,
    report_path: Optional[Union[Path, str]] = None,
    color_spaces: Optional[List[ColorSpace]] = None,
    sections: Optional[List[str]] = None,
) -> None:
    """Generate an HTML report of all your colors and color groups that can be easily shipped or shared with any analysis

    Parameters
    ----------
    camp : Camp
        A Camp object to generate the report from
    report_path : Optional[Union[Path, str]], optional
        Destination path to save the report. Will default to `./<Camp_Name>.html`, by default None
    color_spaces : Optional[List[ColorSpace]], optional
        Order or omit which color spaces are displayed (color section only), by default None
    sections : Optional[List[str]], optional
        Order or omit which sections are displayed. If none are supplied all will be used in order ('colors', 'palettes', 'scales', 'maps'), by default None

    Returns
    -------
    None
    """

    if report_path is None:
        report_path = Path(".") / f"{camp.name}.html"

    PathValidator().validate(report_path)

    html_report = camp_to_html(camp, color_spaces, sections)

    with open(report_path, "w", encoding="UTF-8") as file:
        file.write(html_report)
