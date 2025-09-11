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
    for container in containers:
        stats = container.stats(stream=False)

        cpu_percent = calculate_cpu_percent(stats)
        image = container.image.tags[0] if container.image.tags else "N/A"
        created = container.attrs['Created']
        # ports = container.attrs['NetworkSettings']['Ports']
        mem_usage_mb = stats["memory_stats"]["usage"] / (1024 * 1024)
        containers_stats.append(f"~  Container name: {container.name} \n"
                                f"~  Container status: {container.status} \n"
                                f"~  Parent image: {image} \n"
                                f"~  Time created: {created} \n"
                                f"~  CPU load: {cpu_percent:.2f} % \n"
                                f"~  RAM use: {mem_usage_mb:.2f} MB\n")
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