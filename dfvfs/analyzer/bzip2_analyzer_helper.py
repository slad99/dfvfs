# -*- coding: utf-8 -*-
"""The BZIP2 format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class Bzip2AnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the BZIP2 analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_COMPRESSED_STREAM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BZIP2

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.Specification(self.type_indicator)

    # TODO: add support for signature chains so that we add the 'BZ' at
    # offset 0.

    # BZIP2 compressed steam signature.
    format_specification.AddNewSignature(b'\x31\x41\x59\x26\x53\x59', offset=4)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(Bzip2AnalyzerHelper())
