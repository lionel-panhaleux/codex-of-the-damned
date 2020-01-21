# Codex of the Damned

This site is a compilation of Vampire: the Eternal Struggle strategy resources.
The site is publicly available at [codex-of-the-damned.org](http://www.codex-of-the-damned.org).

Portions of the materials are the copyrights and trademarks of Paradox Interactive AB,
and are used with permission. All rights reserved.
For more information please visit [white-wolf.com](http://www.white-wolf.com).

![Dark Pack](icons/dark-pack.png)

## Contributing

Contributions are welcome. Pull Requests will be merged if they respect the general style.
Issues will be dealt with as quickly as possible.

This site a fully static website using no generator and only a few lines of JS.
This is a voluntary [KISS](https://en.wikipedia.org/wiki/KISS_principle) design,
please refrain from using additional tools or frameworks.

## Useful tools

Convert icons from raster to SVG using `imagemagick` and `potrace`:

```bash
convert -morphology Smooth Octagon:2 clan-ahrimanes.gif clan-ahrimanes.svg
```

Depending on the icon, smoothing may be better or not.
