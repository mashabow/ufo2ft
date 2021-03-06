from fontTools.misc.transform import Transform
from ufo2ft.filters import BaseFilter

import logging


logger = logging.getLogger(__name__)


class FlattenComponentsFilter(BaseFilter):

    def __call__(self, font, glyphSet=None):
        if super(FlattenComponentsFilter, self).__call__(font, glyphSet):
            modified = self.context.modified
            if modified:
                logger.info('Flattened composite glyphs: %i' %
                            len(modified))
            return modified

    def filter(self, glyph):
        flattened = False
        if not glyph.components:
            return flattened
        pen = glyph.getPen()
        for comp in list(glyph.components):
            flattened_tuples = _flattenComponent(self.context.glyphSet, comp)
            if flattened_tuples[0] != (comp.baseGlyph, comp.transformation):
                flattened = True
            glyph.removeComponent(comp)
            for flattened_tuple in flattened_tuples:
                pen.addComponent(*flattened_tuple)
        if flattened:
            self.context.modified.add(glyph.name)
        return flattened


def _flattenComponent(glyphSet, component):
    """Returns a list of tuples (baseGlyph, transform) of nested component."""

    glyph = glyphSet[component.baseGlyph]
    if not glyph.components:
        transformation = Transform(*component.transformation)
        return [(component.baseGlyph, transformation)]

    all_flattened_components = []
    for nested in glyph.components:
        flattened_components = _flattenComponent(glyphSet, nested)
        for i, (_, tr) in enumerate(flattened_components):
            tr = tr.transform(component.transformation)
            flattened_components[i] = (flattened_components[i][0], tr)
        all_flattened_components.extend(flattened_components)
    return all_flattened_components
