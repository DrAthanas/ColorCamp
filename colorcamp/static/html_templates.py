"""HTML templates for _repr_html_ methods and reporting"""

# _repr_html_ template code

MIN_WIDTH = 180
MIN_HEIGHT = 30

HTML_NAME_TEMPLATE = """
<h4 style="
    color: white;
    text-align: center;
    margin: 5px;
    text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
    ">{name}
</h4>"""

HTML_REPR_TEMPLATE = """
<div style="width: {width}px;">
    {name}
    <div style="
            height: {height}px; 
            {color} 
            border: 1px solid black; 
            border-radius: 5px; 
            padding: 5px;
            display: flex; 
            align-items: center; 
            justify-content: center;
            text-align: center;
            color: white;
            font-size: 12px;
            text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
        ">
        {text}
    </div>
</div>
"""

MAP_TABLE_ROW = """
<tr>
    <td>{text}</td>
    <td style="
        width: {width}px; 
        height: {height}px; 
        background-color: {css};
        align-items: center; 
        justify-content: center;
    "></td>
</tr>
"""

# Report HTML Templates
REPORT_TEMPLATE = """<!DOCTYPE html>
<style>
{css}
</style>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>{camp_name}</title>
        <meta name="viewport" content="width=device-width,initial-scale=1.0">
        <meta name="description" content="{description}">
        <meta name="author" content="colorcamp">
        <meta http-equiv="content-language" content="ll-cc">
    </head>
    <body>
        <div class="container">
            <section id="descriptionSection">
                <h1>{camp_name}</h1>
                <p>{description}</p>
            </section>
        </div>
        {sections_html}
    </body>
</html>
"""

SECTION_HTML = """<div class="container">
    <section id="colorNameSection">
        <ul class="colorNameList">
            <h2>{section_name}</h2>
            {content}
        </ul>
        <div class="clearfix"></div>
    </section>
</div>
"""

COLOR_OBJECT_HTML = """<li>
    {header}
    {color_bar}
    {spaces}
</li>
"""

SPACE_HTML = """
<div class="space">
    <div class="name">{name}</div>
    {values}
</div>
"""

VALUE_HTML = '<div class="value">{value}</div>'
