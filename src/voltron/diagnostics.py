import sys
import json
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path
from .core.smbus_engine import BatteryDevice, MockBatteryDevice
from .utils.scanner import find_battery_bus, format_report

# Setup: ensure data/ folder exists at project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(DATA_DIR / "log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Project Voltron: Smart Battery Diagnostic Service")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode without hardware.")
    parser.add_argument("--surgery", action="store_true", help="Attempt to unseal the battery using default keys.")
    args = parser.parse_args()

    logger.info("--- Project Voltron: Smart Battery Diagnostic Service ---")
    
    if args.simulate:
        logger.info("[MODE] Simulation Enabled")
        bus_number = 0
        battery = MockBatteryDevice(bus_number)
    else:
        try:
            import smbus2
        except ImportError:
            logger.error("Error: 'smbus2' library not found. Please run 'uv add smbus2'.")
            sys.exit(1)

        # 1. Bus Discovery
        logger.info("Scanning for Battery SMBus...")
        bus_number = find_battery_bus()
        
        if bus_number is None:
            logger.error("Error: No battery detected at address 0x0B on any I2C bus.")
            logger.info("Ensure i2c-dev module is loaded (sudo modprobe i2c-dev) and you have permission.")
            sys.exit(1)
            
        logger.info(f"Battery found on /dev/i2c-{bus_number}")
        
        try:
            battery = BatteryDevice(bus_number)
        except PermissionError:
            logger.error("Error: Permission denied. Please run with 'sudo'.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error initializing battery: {e}")
            sys.exit(1)

    # 2. Read Data
    try:
        diagnostic_data = {
            "timestamp": datetime.now().isoformat(),
            "bus_number": bus_number,
            "simulation_mode": args.simulate,
            "metrics": {
                "voltage_mv": battery.get_voltage(),
                "current_ma": battery.get_current(),
                "temperature_c": round(battery.get_temperature(), 2),
                "cycle_count": battery.get_cycle_count(),
                "design_capacity_mah": battery.get_design_capacity()
            },
            "status": {
                "pf_bit_set": battery.is_pf_bit_set(),
                "seal_status": battery.get_unseal_status()
            }
        }
        
        # 3. Output Result
        report_json = format_report(diagnostic_data)
        logger.info("\nDiagnostic Report:")
        logger.info(report_json)

        # 4. Surgery Phase
        if args.surgery:
            logger.info("\n" + "="*40)
            logger.info("ENTERING SURGERY MODE")
            logger.info("="*40)
            
            if args.simulate:
                logger.info("[SIMULATION] Pretending to perform unseal surgery...")
                logger.info("[SIMULATION] Unseal SUCCESS!")
            else:
                from core.surgery import BatterySurgery
                surgeon = BatterySurgery(battery)
                surgeon.attempt_unseal()
            logger.info("="*40 + "\n")
        
        # 5. Save to data/reports/
        reports_dir = DATA_DIR / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        filename = reports_dir / f"diag_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            f.write(report_json)
        logger.info(f"\nReport saved to {filename}")
        
        # 6. Optional Cloud Sync
        api_endpoint = os.getenv("VOLTRON_API_ENDPOINT")
        if api_endpoint:
            from utils.cloud_sync import upload_report
            logger.info("\nSyncing with Cloud Dashboard...")
            sync_res = upload_report(filename, api_endpoint, os.getenv("VOLTRON_API_KEY"))
            if sync_res["success"]:
                logger.info("Cloud Sync Successful!")
            else:
                logger.error(f"Cloud Sync Failed: {sync_res['error']}")
        
        battery.close()

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
