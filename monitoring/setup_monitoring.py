import sys
import docker
from docker import errors
from typing import Optional

import logger_setup.logger as lc

if __name__ == "__main__":
    lc.logger.error("This file cannot be run as main!")
    print("\nThis file cannot be run as main!")
    sys.exit()

try:
    client = docker.from_env()
except errors.DockerException:
    client = None
    lc.logger.error("Docker is not working right now!")


def get_container_metrics() -> list[str]:
    """
    Retrieve metrics for all running Docker containers.

    For each container, this function collects:
        - container name
        - container status
        - parent image
        - creation time
        - CPU usage percentage
        - RAM usage in MB

    Returns:
        list[str]: A list of formatted strings containing metrics
        for each container.
    """
    containers = client.containers.list()
    containers_stats = []
    
    total_cpu = 0.0
    total_mem = 0.0
    total_mem_limit = 0.0
    total_blk_read = 0
    total_blk_write = 0
    total_rx = 0.0
    total_tx = 0.0
    total_restarts = 0

    for container in containers:
        stats = container.stats(stream=False)

        cpu_percent = calculate_cpu_percent(stats)
        image = container.image.tags[0] if container.image.tags else "N/A"
        created = container.attrs['Created']
        mem_usage = stats["memory_stats"]["usage"] - stats["memory_stats"]["stats"].get("cache", 0)
        mem_usage_mb = mem_usage / (1024 * 1024)
        
        mem_limit_mb = stats["memory_stats"]["limit"] / (1024 * 1024)
        mem_percent = (mem_usage / stats["memory_stats"]["limit"]) * 100 if stats["memory_stats"]["limit"] > 0 else 0

        blk_read, blk_write = 0, 0
        if stats["blkio_stats"]["io_service_bytes_recursive"]:
            blk_read = stats["blkio_stats"]["io_service_bytes_recursive"][0]["value"]
            if len(stats["blkio_stats"]["io_service_bytes_recursive"]) > 1:
                blk_write = stats["blkio_stats"]["io_service_bytes_recursive"][1]["value"]

        rx_bytes, tx_bytes = 0, 0
        if "networks" in stats:
            rx_bytes = round(sum(net["rx_bytes"] for net in stats["networks"].values()) / 1024, 2)
            tx_bytes = round(sum(net["tx_bytes"] for net in stats["networks"].values()) / 1024, 2)

        restart_count = container.attrs.get("RestartCount", 0)

        containers_stats.append(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
            f"~  Container name: {container.name}\n"
            f"~  Container status: {container.status}\n"
            f"~  Parent image: {image}\n"
            f"~  Time created: {created}\n"
            f"~  CPU load: {cpu_percent:.2f}%\n"
            f"~  RAM use: {mem_usage_mb:.2f} MB / {mem_limit_mb:.2f} MB ({mem_percent:.2f}%)\n"
            f"~  Disk IO: Read {blk_read} B / Write {blk_write} B\n"
            f"~  Network IO: RX {rx_bytes} KB / TX {tx_bytes} KB\n"
            f"~  Restart count: {restart_count}\n"
        )
        
        total_cpu += cpu_percent
        total_mem += mem_usage_mb
        total_mem_limit += mem_limit_mb
        total_blk_read += blk_read
        total_blk_write += blk_write
        total_rx += rx_bytes
        total_tx += tx_bytes
        total_restarts += restart_count
    
    containers_stats.append(
        f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        f"           TOTAL METRICS FOR ALL CONTAINERS         \n\n"
        f"~  CPU load (sum): {total_cpu:.2f}%\n"
        f"~  RAM use (sum): {total_mem:.2f} MB / {total_mem_limit:.2f} MB\n"
        f"~  Disk IO (sum): Read {total_blk_read} B / Write {total_blk_write} B\n"
        f"~  Network IO (sum): RX {total_rx:.2f} KB / TX {total_tx:.2f} KB\n"
        f"~  Restarts (sum): {total_restarts}\n"
    )   
    
    return containers_stats


def calculate_cpu_percent(stats) -> float:
    """
    Calculate CPU usage percentage for a Docker container.

    Args:
        stats (dict): The container statistics dictionary
            obtained from `container.stats(stream=False)`.

    Returns:
        float: The CPU usage percentage.
    """
    cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
        stats["precpu_stats"]["cpu_usage"]["total_usage"]
    system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
        stats["precpu_stats"]["system_cpu_usage"]

    if system_delta > 0:
        return (cpu_delta / system_delta) * \
            len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"]) * 100.0
    return 0.0


def get_container_status_real_time() -> Optional[str]:
    """
    Check running containers for high resource usage in real time.

    This function monitors all containers and reports if:
        - CPU usage exceeds 50%
        - Memory usage exceeds 500 MB

    Returns:
        str or int: Warning message string if any container exceeds
        thresholds; otherwise, returns None.
    """
    containers = client.containers.list()

    for container in containers:
        stats = container.stats(stream=False)
        cpu_percent = calculate_cpu_percent(stats)

        if float(cpu_percent) > 50.00:
            return f"The container {container.name} uses more than 50% \
                of the available processor resources on the host"

        mem_usage_mb = stats["memory_stats"]["usage"] / (1024 * 1024)
        if float(mem_usage_mb) > 500.00:
            return f"The container {container.name} uses \
                500 MB of the available RAM resources on the host"
    return None