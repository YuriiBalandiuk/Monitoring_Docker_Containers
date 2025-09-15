import pytest
from unittest.mock import MagicMock, patch
import monitoring.setup_monitoring


def test_calculate_cpu_percent_basic():
    stats = {
        "cpu_stats": {
            "cpu_usage": {"total_usage": 200, "percpu_usage": [100, 100]},
            "system_cpu_usage": 400,
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": 100, "percpu_usage": [50, 50]},
            "system_cpu_usage": 200,
        }
    }
    result = monitoring.setup_monitoring.calculate_cpu_percent(stats)
    assert result == 100.0  # (100 / 200) * 2 * 100 = 100%

def test_calculate_cpu_percent_zero_system_delta():
    stats = {
        "cpu_stats": {"cpu_usage": {"total_usage": 200, "percpu_usage": [100,100]}, "system_cpu_usage": 400},
        "precpu_stats": {"cpu_usage": {"total_usage": 100, "percpu_usage": [50,50]}, "system_cpu_usage": 400}
    }
    result = monitoring.setup_monitoring.calculate_cpu_percent(stats)
    assert result == 0.0


@patch("monitoring.setup_monitoring.client")
def test_get_container_metrics(mock_client):
    mock_container = MagicMock()
    mock_container.name = "test_container"
    mock_container.status = "running"
    mock_container.image.tags = ["test_image:latest"]
    mock_container.attrs = {"Created": "2025-01-01T00:00:00"}
    mock_container.stats.return_value = {
        "memory_stats": {"usage": 104857600},
        "cpu_stats": {
            "cpu_usage": {"total_usage": 200, "percpu_usage": [100,100]},
            "system_cpu_usage": 400
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": 100, "percpu_usage": [50,50]},
            "system_cpu_usage": 200
        }
    }
    mock_client.containers.list.return_value = [mock_container]

    metrics = monitoring.setup_monitoring.get_container_metrics()
    assert len(metrics) == 1
    assert "test_container" in metrics[0]
    assert "test_image:latest" in metrics[0]
    assert "RAM use: 100.00 MB" in metrics[0]


@patch("monitoring.setup_monitoring.client")
def test_get_container_status_real_time_cpu(mock_client):
    mock_container = MagicMock()
    mock_container.name = "high_cpu"
    mock_container.stats.return_value = {
        "memory_stats": {"usage": 1048576},
        "cpu_stats": {
            "cpu_usage": {"total_usage": 200, "percpu_usage": [100,100]},
            "system_cpu_usage": 200
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": 0, "percpu_usage": [0,0]},
            "system_cpu_usage": 100
        }
    }
    mock_client.containers.list.return_value = [mock_container]

    status = monitoring.setup_monitoring.get_container_status_real_time()
    assert "high_cpu" in status
    assert "50%" in status


@patch("monitoring.setup_monitoring.client")
def test_get_container_status_real_time_mem(mock_client):
    mock_container = MagicMock()
    mock_container.name = "high_mem"
    mock_container.stats.return_value = {
        "memory_stats": {"usage": 600 * 1024 * 1024},
        "cpu_stats": {"cpu_usage": {"total_usage": 0, "percpu_usage": [0,0]}, "system_cpu_usage": 100},
        "precpu_stats": {"cpu_usage": {"total_usage": 0, "percpu_usage": [0,0]}, "system_cpu_usage": 100}
    }
    mock_client.containers.list.return_value = [mock_container]

    status = monitoring.setup_monitoring.get_container_status_real_time()
    assert "high_mem" in status
    assert "500 MB" in status


@patch("monitoring.setup_monitoring.client")
def test_get_container_status_real_time_none(mock_client):
    mock_container = MagicMock()
    mock_container.name = "normal"
    mock_container.stats.return_value = {
        "memory_stats": {"usage": 100 * 1024 * 1024},
        "cpu_stats": {"cpu_usage": {"total_usage": 0, "percpu_usage": [0,0]}, "system_cpu_usage": 100},
        "precpu_stats": {"cpu_usage": {"total_usage": 0, "percpu_usage": [0,0]}, "system_cpu_usage": 100}
    }
    mock_client.containers.list.return_value = [mock_container]

    status = monitoring.setup_monitoring.get_container_status_real_time()
    assert status is None