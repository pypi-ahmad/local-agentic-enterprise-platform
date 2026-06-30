import re
import subprocess
from dataclasses import dataclass


@dataclass(slots=True)
class GPUStatus:
    available: bool
    name: str = ""
    total_vram_mb: int = 0
    used_vram_mb: int = 0
    utilization_percent: int = 0


class GPUMonitor:
    """Collects NVIDIA GPU telemetry through nvidia-smi."""

    @staticmethod
    def read_status() -> GPUStatus:
        try:
            output = subprocess.check_output(["nvidia-smi"], text=True, timeout=5)
        except Exception:
            return GPUStatus(available=False)

        name_match = re.search(r"\|\s+\d+\s+([^|]+?)\s+\|", output)
        mem_match = re.search(r"(\d+)MiB\s*/\s*(\d+)MiB", output)
        util_match = re.search(r"(\d+)%\s+Default", output)

        return GPUStatus(
            available=True,
            name=name_match.group(1).strip() if name_match else "Unknown",
            total_vram_mb=int(mem_match.group(2)) if mem_match else 0,
            used_vram_mb=int(mem_match.group(1)) if mem_match else 0,
            utilization_percent=int(util_match.group(1)) if util_match else 0,
        )
