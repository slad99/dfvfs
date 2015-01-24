# -*- coding: utf-8 -*-
"""The data range file-like object."""

import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver


class DataRange(file_io.FileIO):
  """Class that implements a file-like object that maps an in-file data range.

     The data range object allows to expose a single partition within
     a full disk image as a separate file-like object by mapping
     the data range (offset and size) fo the volume on top of the full disk
     image.
  """

  def __init__(self, resolver_context, file_object=None):
    """Initializes the file-like object.

       If the file-like object is chained do not separately use the parent
       file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_object: optional parent file-like object. The default is None.
    """
    super(DataRange, self).__init__(resolver_context)
    self._file_object = file_object
    self._current_offset = 0

    if file_object:
      self._file_object_set_in_init = True
      self._range_offset = 0
      self._range_size = file_object.get_size()
    else:
      self._file_object_set_in_init = False
      self._range_offset = -1
      self._range_size = -1
    self._is_open = False

  def SetRange(self, range_offset, range_size):
    """Sets the data range (offset and size).

    The data range is used to map a range of data within one file
    (e.g. a single partition within a full disk image) as a file-like object.

    Args:
      range_offset: the start offset of the data range.
      range_size: the size of the data range.

    Raises:
      IOError: if the file-like object is already open.
      ValueError: if the range offset or range size is invalid.
    """
    if self._is_open:
      raise IOError(u'Already open.')

    if range_offset < 0:
      raise ValueError(
          u'Invalid range offset: {0:d} value out of bounds.'.format(
              range_offset))

    if range_size < 0:
      raise ValueError(
          u'Invalid range size: {0:d} value out of bounds.'.format(
              range_size))

    self._range_offset = range_offset
    self._range_size = range_size
    self._current_offset = 0

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def open(self, path_spec=None, mode='rb'):
    """Opens the file-like object.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      IOError: if the open file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification or mode is invalid.
    """
    if not self._file_object_set_in_init and not path_spec:
      raise ValueError(u'Missing path specfication.')

    if mode != 'rb':
      raise ValueError(u'Unsupport mode: {0:s}.'.format(mode))

    if self._is_open:
      raise IOError(u'Already open.')

    if not self._file_object_set_in_init:
      if not path_spec.HasParent():
        raise errors.PathSpecError(
            u'Unsupported path specification without parent.')

      range_offset = getattr(path_spec, 'range_offset', None)
      range_size = getattr(path_spec, 'range_size', None)

      if range_offset is None or range_size is None:
        raise errors.PathSpecError(
            u'Path specification missing range offset and range size.')

      self.SetRange(range_offset, range_size)
      self._file_object = resolver.Resolver.OpenFileObject(
          path_spec.parent, resolver_context=self._resolver_context)

    self._is_open = True

  def close(self):
    """Closes the file-like object.

       If the file-like object was passed in the init function
       the data range file-like object does not control the file-like object
       and should not actually close it.

    Raises:
      IOError: if the close failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    self._resolver_context.RemoveFileObject(self)

    if not self._file_object_set_in_init:
      self._file_object.close()
      self._file_object = None
      self._range_offset = -1
      self._range_size = -1

    self._is_open = False

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

       The function will read a byte string of the specified size or
       all of the remaining data if no size was specified.

    Args:
      size: optional integer value containing the number of bytes to read.
            Default is all remaining data (None).

    Returns:
      A byte string containing the data read.

    Raises:
      IOError: if the read failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._range_offset < 0 or self._range_size < 0:
      raise IOError(u'Invalid data range.')

    if self._current_offset < 0:
      raise IOError(
          u'Invalid current offset: {0:d} value less than zero.'.format(
              self._current_offset))

    if self._current_offset >= self._range_size:
      return ''

    if size is None:
      size = self._range_size
    if self._current_offset + size > self._range_size:
      size = self._range_size - self._current_offset

    self._file_object.seek(
        self._range_offset + self._current_offset, os.SEEK_SET)

    data = self._file_object.read(size)

    self._current_offset += len(data)

    return data

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: the offset to seek.
      whence: optional value that indicates whether offset is an absolute
              or relative position within the file. Default is SEEK_SET.

    Raises:
      IOError: if the seek failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._current_offset < 0:
      raise IOError(
          u'Invalid current offset: {0:d} value less than zero.'.format(
              self._current_offset))

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._range_size
    elif whence != os.SEEK_SET:
      raise IOError(u'Unsupported whence.')
    if offset < 0:
      raise IOError(u'Invalid offset value less than zero.')
    self._current_offset = offset

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._current_offset

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._range_size
