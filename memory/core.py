# Libraries and Core Files
import ctypes
import ctypes.wintypes
import logging
import os

import pymem
from ReadWriteMemory import Process, ReadWriteMemory, ReadWriteMemoryError

logger = logging.getLogger(__name__)


class LocProcess(Process):
    def __init__(self, *args, **kwargs):
        super(LocProcess, self).__init__(*args, **kwargs)

    def _read_val(self, lp_base_address: int, lp_buffer):
        bytes_read = ctypes.c_size_t()
        if ctypes.windll.kernel32.ReadProcessMemory(
            self.handle,
            lp_base_address,
            ctypes.byref(lp_buffer),
            ctypes.sizeof(lp_buffer),
            ctypes.byref(bytes_read),
        ):
            return lp_buffer.value
        raise ReferenceError(
            lp_base_address
        )  # ctypes.WinError(ctypes.get_last_error())

    def read_float(self, lp_base_address: int):
        lp_buffer = ctypes.c_float()
        return self._read_val(lp_base_address=lp_base_address, lp_buffer=lp_buffer)

    def read_double(self, lp_base_address: int):
        lp_buffer = ctypes.c_double()
        return self._read_val(lp_base_address=lp_base_address, lp_buffer=lp_buffer)

    def read_s8(self, lp_base_address: int):
        lp_buffer = ctypes.c_int8()
        return self._read_val(lp_base_address=lp_base_address, lp_buffer=lp_buffer)

    def read_u8(self, lp_base_address: int):
        lp_buffer = ctypes.c_uint8()
        return self._read_val(lp_base_address=lp_base_address, lp_buffer=lp_buffer)

    def read_s16(self, lp_base_address: int):
        lp_buffer = ctypes.c_int16()
        return self._read_val(lp_base_address=lp_base_address, lp_buffer=lp_buffer)

    def read_u16(self, lp_base_address: int):
        lp_buffer = ctypes.c_uint16()
        return self._read_val(lp_base_address=lp_base_address, lp_buffer=lp_buffer)

    def read_s32(self, lp_base_address: int):
        lp_buffer = ctypes.c_int32()
        return self._read_val(lp_base_address=lp_base_address, lp_buffer=lp_buffer)

    def read_u32(self, lp_base_address: int):
        lp_buffer = ctypes.c_uint32()
        return self._read_val(lp_base_address=lp_base_address, lp_buffer=lp_buffer)

    def read_s64(self, lp_base_address: int):
        lp_buffer = ctypes.c_int64()
        return self._read_val(lp_base_address=lp_base_address, lp_buffer=lp_buffer)

    def read_u64(self, lp_base_address: int):
        lp_buffer = ctypes.c_uint64()
        return self._read_val(lp_base_address=lp_base_address, lp_buffer=lp_buffer)


# Process Permissions
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020

MAX_PATH = 260


class EvolandMemory(ReadWriteMemory):
    def __init__(self, *args, **kwargs):
        super(EvolandMemory, self).__init__(*args, **kwargs)
        self.process = LocProcess()

    def initialize(
        self, process_name: str = "Evoland.exe", dll_name: str = "libhl.dll"
    ):
        pm = pymem.Pymem(process_name)
        self.base_addr = pymem.process.module_from_name(
            pm.process_handle, dll_name
        ).lpBaseOfDll
        logger.debug(
            f"Base address of {dll_name} in {process_name}: {hex(self.base_addr)}"
        )

        self.process = self._get_process_by_name(process_name)
        self.process.open()

    def _get_process_by_name(self, process_name: str | bytes) -> LocProcess:
        """
        :description: Get the process by the process executabe\'s name and return a Process object.

        :param process_name: The name of the executable file for the specified process for example, my_program.exe.

        :return: A Process object containing the information from the requested Process.
        """
        if not process_name.endswith(".exe"):
            self.process.name = f"{process_name}.exe"

        process_ids = self.enumerate_processes()

        for process_id in process_ids:
            self.process.handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION, False, process_id
            )
            if self.process.handle:
                image_file_name = (ctypes.c_char * MAX_PATH)()
                if (
                    ctypes.windll.psapi.GetProcessImageFileNameA(
                        self.process.handle, image_file_name, MAX_PATH
                    )
                    > 0
                ):
                    filename = os.path.basename(image_file_name.value)
                    if filename.decode("utf-8") == process_name:
                        self.process.pid = process_id
                        self.process.name = process_name
                        return self.process
                self.process.close()

        raise ReadWriteMemoryError(f'Process "{self.process.name}" not found!')


_mem = EvolandMemory()
_mem.initialize("Evoland.exe", "libhl.dll")


def handle() -> EvolandMemory:
    return _mem
