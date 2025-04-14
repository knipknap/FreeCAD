import os

__dir__ = os.path.dirname(__file__)
resource_dir = os.path.join(__dir__, 'resources')
icon_dir = os.path.join(resource_dir, 'icons')
translations_dir = os.path.abspath(os.path.join(resource_dir, 'translations'))

builtin_tool_dir = os.path.abspath(os.path.join(__dir__, '..', '..', 'Tools'))
builtin_bit_dir = os.path.join(builtin_tool_dir, 'Bit')
builtin_shape_dir = os.path.join(builtin_tool_dir, 'Shape')
builtin_library_dir = os.path.join(builtin_tool_dir, 'Library')
