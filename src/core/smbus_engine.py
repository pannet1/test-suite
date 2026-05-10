import time
import logging

logger = logging.getLogger(__name__)

try:
    import smbus2
except ImportError:
    smbus2 = None

class BatteryDevice:
    """
    Handles communication with a Smart Battery over SMBus.
    Standard Smart Battery Data (SBD) registers are mapped here.
    """
    BATTERY_ADDRESS = 0x0B

    # Standard SBD Registers
    REG_TEMPERATURE = 0x08
    REG_VOLTAGE = 0x09
    REG_CURRENT = 0x0A
    REG_REMAINING_CAPACITY = 0x0F
    REG_FULL_CHARGE_CAPACITY = 0x10
    REG_CYCLE_COUNT = 0x17
    REG_DESIGN_CAPACITY = 0x18
    
    # TI BQ Specific Registers
    REG_SAFETY_STATUS = 0x51
    REG_OPERATION_STATUS = 0x54

    def __init__(self, bus_number):
        if smbus2 is None:
            raise ImportError("smbus2 library is required for hardware communication.")
        self.bus_number = bus_number
        self.bus = smbus2.SMBus(bus_number)

    def _read_word(self, register):
        try:
            return self.bus.read_word_data(self.BATTERY_ADDRESS, register)
        except Exception as e:
            raise IOError(f"Failed to read register {hex(register)}: {e}")

    def get_temperature(self):
        # Temperature is in 0.1K
        temp_k = self._read_word(self.REG_TEMPERATURE)
        return (temp_k / 10.0) - 273.15  # Convert to Celsius

    def get_voltage(self):
        # Voltage in mV
        return self._read_word(self.REG_VOLTAGE)

    def get_current(self):
        # Current in mA (signed integer)
        val = self._read_word(self.REG_CURRENT)
        if val > 32767:
            val -= 65536
        return val

    def get_remaining_capacity(self):
        return self._read_word(self.REG_REMAINING_CAPACITY)

    def get_full_charge_capacity(self):
        return self._read_word(self.REG_FULL_CHARGE_CAPACITY)

    def get_cycle_count(self):
        return self._read_word(self.REG_CYCLE_COUNT)

    def get_design_capacity(self):
        return self._read_word(self.REG_DESIGN_CAPACITY)

    def get_safety_status(self):
        """Read SafetyStatus (0x51) for TI BQ series."""
        return self.bus.read_i2c_block_data(self.BATTERY_ADDRESS, self.REG_SAFETY_STATUS, 4)

    def get_operation_status(self):
        """Read OperationStatus (0x54) for TI BQ series."""
        # Returns a 4-byte block usually
        return self.bus.read_i2c_block_data(self.BATTERY_ADDRESS, self.REG_OPERATION_STATUS, 4)

    def get_unseal_status(self):
        """
        Read OperationStatus (0x54) to determine the seal state of TI BQ chips.
        Bits 11 and 10 of OperationStatus:
        0,1 = Full Access
        1,0 = Unsealed
        1,1 = Sealed
        """
        try:
            status = self.get_operation_status()
            # OperationStatus is often a 32-bit value (4 bytes).
            # We'll parse the relevant bits from the first two bytes.
            combined_status = int.from_bytes(status[:2], byteorder='little')
            
            # Bits 11:10
            seal_bits = (combined_status >> 10) & 0x03
            
            if seal_bits == 0b01:
                return "Full Access"
            elif seal_bits == 0b10:
                return "Unsealed"
            elif seal_bits == 0b11:
                return "Sealed"
            else:
                return "Unknown"
        except Exception:
            return "Error reading status"

    def is_pf_bit_set(self):
        """
        Checks if the Permanent Failure (PF) bit is set.
        In many TI BQ chips, SafetyStatus (0x51), Bit 12 represents PF.
        """
        try:
            status = self.get_safety_status()
            # SafetyStatus is usually 2 or 4 bytes. 
            combined_status = int.from_bytes(status[:2], byteorder='little')
            return bool(combined_status & (1 << 12))
        except:
            return False

class MockBatteryDevice:
    """
    Simulates a battery for local testing without SMBus hardware.
    """
    def __init__(self, bus_number=0):
        self.bus_number = bus_number
        logger.info(f"[SIMULATION] Initializing Mock Battery on bus {bus_number}")

    def get_temperature(self):
        return 25.5

    def get_voltage(self):
        return 12600

    def get_current(self):
        return -150

    def get_remaining_capacity(self):
        return 3200

    def get_full_charge_capacity(self):
        return 4200

    def get_cycle_count(self):
        return 42

    def get_design_capacity(self):
        return 4400

    def get_safety_status(self):
        # Simulate a PF bit set (Bit 12) or not
        # Return 4 bytes
        return b'\x00\x10\x00\x00' # Bit 12 is set (0x1000)

    def get_operation_status(self):
        # Simulate "Unsealed" status (Bits 11:10 = 1,0)
        # 1,0 in bits 11:10 of a 16-bit word is 0x0800
        return b'\x00\x08\x00\x00'

    def get_unseal_status(self):
        return "Unsealed (Simulated)"

    def is_pf_bit_set(self):
        return True

    def close(self):
        pass
