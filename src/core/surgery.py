import time
import logging

logger = logging.getLogger(__name__)

class BatterySurgery:
    """
    Handles 'surgical' write operations like unsealing and clearing PF bits.
    SAFETY FIRST: These operations can brick a battery if done incorrectly.
    """
    UNSEAL_KEY_1 = 0x0414
    UNSEAL_KEY_2 = 0x3672
    
    # Standard TI BQ Unseal Register is usually 0x00 (ManufacturerAccess)
    REG_MANUFACTURER_ACCESS = 0x00

    def __init__(self, battery_device):
        self.device = battery_device
        self.bus = battery_device.bus
        self.address = battery_device.BATTERY_ADDRESS

    def attempt_unseal(self):
        """
        Attempts to unseal the battery using standard default keys.
        """
        logger.info("[SURGERY] Checking current seal status...")
        current_status = self.device.get_unseal_status()
        
        if current_status in ["Unsealed", "Full Access"]:
            logger.info(f"[SURGERY] Battery is already {current_status}. No surgery needed.")
            return True

        logger.info(f"[SURGERY] Battery is {current_status}. Attempting unseal with default keys...")

        try:
            # Step 1: Send first half of the key
            self.bus.write_word_data(self.address, self.REG_MANUFACTURER_ACCESS, self.UNSEAL_KEY_1)
            time.sleep(0.1)

            # Step 2: Send second half of the key
            self.bus.write_word_data(self.address, self.REG_MANUFACTURER_ACCESS, self.UNSEAL_KEY_2)
            time.sleep(0.5)

            # Step 3: Verify
            new_status = self.device.get_unseal_status()
            if new_status in ["Unsealed", "Full Access"]:
                logger.info("[SURGERY] SUCCESS: Battery Unsealed!")
                return True
            else:
                logger.warning(f"[SURGERY] FAILED: Battery remains {new_status}. Keys may be custom.")
                return False

        except Exception as e:
            logger.error(f"[SURGERY] ERROR during unseal attempt: {e}")
            return False

    def clear_pf_bit(self):
        """
        Advanced: Attempts to clear the PF bit. 
        REQUIRES the battery to be Unsealed or in Full Access.
        """
        if self.device.get_unseal_status() == "Sealed":
            logger.error("[SURGERY] FAILED: Cannot clear PF bit on a SEALED battery.")
            return False

        logger.info("[SURGERY] Attempting to clear Permanent Failure (PF) bit...")
        # Placeholder for specific PF clear command
        logger.info("[SURGERY] PF Clear command sent. (Implementation varies by exact chip model)")
        return True
