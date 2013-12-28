#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The tar extracted file-like object implementation."""

# Note: that tarfile.ExFileObject is not POSIX compliant for seeking
# beyond the file size, hence it is wrapped in an instance of file_io.FileIO.

import os

# This is necessary to prevent a circular import.
import pyvfs.vfs.manager

from pyvfs.file_io import file_io


class TarFile(file_io.FileIO):
  """Class that implements a file-like object using tarfile."""

  def __init__(self, tar_info=None, tar_file_object=None):
    """Initializes the file-like object.

    Args:
      tar_info: optional tar info object (instance of tarfile.TarInfo).
                The default is None.
      tar_file_object: optional extracted file-like object (instance of
                       tarfile.ExFileObject). The default is None.

    Raises:
      ValueError: if tar_file_object provided but tar_info is not.
    """
    if tar_file_object is not None and tar_info is None:
      raise ValueError(
          u'Tar extracted file object provided without corresponding info '
          u'object.')

    super(TarFile, self).__init__()
    self._tar_info = tar_info
    self._tar_file_object = tar_file_object
    self._current_offset = 0
    self._size = 0

    if tar_file_object:
      self._tar_file_object_set_in_init = True
    else:
      self._tar_file_object_set_in_init = False
    self._is_open = False

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional the path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      IOError: if the open file-like object could not be opened.
      ValueError: if the path specification or mode is invalid.
    """
    if not self._tar_file_object_set_in_init and not path_spec:
      raise ValueError(u'Missing path specfication.')

    if mode != 'rb':
      raise ValueError(u'Unsupport mode: {0:s}.'.format(mode))

    if self._is_open:
      raise IOError(u'Already open.')

    if not self._tar_file_object_set_in_init:
      file_system = pyvfs.vfs.manager.FileSystemManager.OpenFileSystem(
          path_spec)

      file_entry = file_system.GetFileEntryByPathSpec(path_spec)

      self._tar_info = file_entry.GetTarInfo()
      self._tar_file_object = file_entry.GetFileObject()

    self._current_offset = 0
    self._size = self._tar_info.size
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

    if not self._tar_file_object_set_in_init:
      self._tar_file_object.close()
      self._tar_file_object = None
      self._tar_info = None

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

    if self._current_offset < 0:
      raise IOError(u'Invalid current offset value less than zero.')

    if self._current_offset > self._size:
      return ''

    if size is None or self._current_offset + size > self._size:
      size = self._size - self._current_offset

    self._tar_file_object.seek(self._current_offset, os.SEEK_SET)

    data = self._tar_file_object.read(size)

    # It is possible the that returned data size is not the same as the
    # requested data size. At this layer we don't care and this discrepancy
    # should be dealt with on a higher layer if necessary.
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

    if not self._is_open:
      raise IOError(u'Not opened.')

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._size
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

    return self._size
