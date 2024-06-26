# ColorCamp
___________
|  |  | 
| --- | --- |
| Testing | [![CI - Test](https://github.com/DrAthanas/ColorCamp/actions/workflows/python-package.yml/badge.svg)](https://github.com/DrAthanas/ColorCamp/actions/workflows/python-package.yml) [![codecov](https://codecov.io/gh/DrAthanas/ColorCamp/coverage.svg?branch=main)](https://codecov.io/gh/DrAthanas/ColorCamp) |
| Package | [![PyPI Latest Release](https://img.shields.io/pypi/v/colorcamp.svg)](https://pypi.org/project/colorcamp/) |
| Meta | [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/DrAthanas/ColorCamp/blob/main/LICENSE)|

The strategic use of color in branding, marketing, and data analytics is a powerful tool that elicits emotions and simplifies comprehension of complex information. Color choice influences how audiences feel about your message, and it can make intricate data more accessible. ColorCamp is a clean way of dealing with colors, palettes, mappings, and scales, and by storing human readable metadata allow more cohesive color choices.  

> A group of geese is a gaggle, an assembly of musicians is a band, a collective of lions is a pride. This package introduces that a collection of colors is a camp! Welcome to Color Camp!

## Example

```python
import colorcamp as cc

# Working with colors
sky_hex = cc.Hex('#15AAFF', name = 'sky')

# is sky_hex a string
isinstance(sky_hex, str)
# > True

# Easily convert to different color spaces 
sky_hsl = sky_hex.to_hsl()
sky_rgb = sky_hex.to_rgb()

# These colors don't share equality but are comparable
sky_hex == sky_hsl
# > False
sky_hex.equivalence(sky_hsl)
# > True
sky_hex == "#15AAFF"
# > True

# Working with color groups
bright_colors = cc.Palette(
    colors = [
        cc.Hex('#15AAFF', name = 'sky'),
        cc.Hex('#FFAA15', name = 'mustard'),
        cc.Hex('#15FFAA', name = 'lime'),
        cc.Hex('#FF15AA', name = 'pink'),
    ],
    name = 'bright_and_sunny'
)

# Palettes are extended tuples
isinstance(bright_colors, tuple)
# > True

# Can be easily saved and shared
bright_colors.dump_json("./bright_colors.json")

# Use these in your favorite plotting packages!
import seaborn as sns
tips = sns.load_dataset("tips")

sns.scatterplot(
    data=tips, 
    x="total_bill", 
    y="tip", 
    hue="time", 
    palette=bright_colors
)

```

See more detailed examples [here](examples)!

## Core tenets
* Provide additional context to colors so they can be used to convey consistent information
* The colors should be immediately recognized by other applications (e.g. a string, tuple, or dictionary) without additional calls
* Easy to import/export to and from multiple sources and frameworks
* Be as lightweight and portable as possible with minimal to no dependencies 

## Installation
The source code is currently hosted on GitHub at:
https://github.com/DrAthanas/ColorCamp

Binary installers for the latest released version are available at the [Python
Package Index (PyPI)](https://pypi.org/project/colorcamp).

```sh
# from PyPI
pip install colorcamp
```

## Dependencies
python ^3.9, that's it!


