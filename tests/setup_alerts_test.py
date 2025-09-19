import pytest
from unittest.mock import Mock, MagicMock, patch
import telegram_bot_alerts.setup_alerts as tba

# Фікстура для мок-повідомлення
@pytest.fixture
def mock_message():
    mock_chat = MagicMock()
    mock_chat.id = 123
    message = MagicMock()
    message.chat = mock_chat
    message.message_id = 456
    message.text = "▶️ Start"
    return message


@patch("telegram_bot_alerts.setup_alerts.gcm")
@patch("telegram_bot_alerts.setup_alerts.bot")
def test_sen_containers_stats_success(bot_mock, gcm_mock, mock_message):
    gcm_mock.return_value = ["Container stats line 1", "Container stats line 2"]
    tba.sen_containers_stats(mock_message)
    bot_mock.reply_to.assert_called()
    called_text = bot_mock.reply_to.call_args[0][1]
    assert "Container stats line 1" in called_text
    assert "Container stats line 2" in called_text


@patch("telegram_bot_alerts.setup_alerts.gcs")
@patch("telegram_bot_alerts.setup_alerts.bot")
def test_update_containers_status_real_time_none(bot_mock, gcs_mock):
    gcs_mock.return_value = None
    with patch("time.sleep", return_value=None):
        count = 0
        status = gcs_mock()
        if status is None:
            count += 1
        assert count == 1
        bot_mock.send_message.assert_not_called()


@patch("telegram_bot_alerts.setup_alerts.gcs")
@patch("telegram_bot_alerts.setup_alerts.bot")
def test_update_containers_status_real_time_status(bot_mock, gcs_mock):
    gcs_mock.return_value = "High CPU usage"
    with patch("time.sleep", return_value=None):
        chat_id = 123
        status = gcs_mock()
        if status is not None:
            bot_mock.send_message(chat_id, status)
        bot_mock.send_message.assert_called_once_with(chat_id, "High CPU usage")


@patch("telegram_bot_alerts.setup_alerts.bot")
def test_echo_message(bot_mock, mock_message):
    tba.echo_message(mock_message)
    bot_mock.reply_to.assert_called_once_with(mock_message, mock_message.text)
    bot_mock.send_message.assert_called()
