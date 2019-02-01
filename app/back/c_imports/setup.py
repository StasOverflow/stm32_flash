from distutils.core import setup, Extension
import os

STM32FLASH_FOLDER_NAME = 'stm32flash'

dir_path = os.path.dirname(os.path.realpath(__file__))
stm32_flash_path = os.path.join(dir_path, STM32FLASH_FOLDER_NAME)

# every 0th element of a 3-tuple is a subdirectory
listing = [x[0] for x in os.walk(stm32_flash_path)]

includes = [dir_path]
includes.extend(listing)


def in_st_folder(souce_code_flie):
    return os.path.join(STM32FLASH_FOLDER_NAME, souce_code_flie)


objects = [
    'stm_py.c',
    'dev_table.c',
    'i2c.c',
    'init.c',
    # 'main.c',
    'port.c',
    'serial_common.c',
    'serial_platform.c',
    'stm32.c',
    'utils.c',
    ]


parser_objects = [
    in_st_folder(os.path.join('parsers', 'binary.c')),
    in_st_folder(os.path.join('parsers', 'hex.c')),
]

wrapped_objects = [in_st_folder(x) for x in objects]
wrapped_objects.extend(parser_objects)
print('---------------------------------\n', wrapped_objects, '\n------------------------------------\n')


setup(
    name='stm32_flash',
    version='1.0',
    ext_modules=[
        Extension(
            'stm32_flash',
            wrapped_objects,
            include_dirs=includes
            )
        ]
    )
