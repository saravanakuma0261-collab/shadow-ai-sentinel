import logging
from app.config import settings
from app.db import repository
from app.db.models import Finding, AlertLog

logger = logging.getLogger(__name__)

def check_and_send_alerts(finding: Finding):
    """
    Evaluates a new finding against alert rules (e.g. Critical tier)
    and dispatches notifications via Slack/Email if configured.
    """
    if finding.risk_tier not in ["critical", "high"]:
        return

    # Slack Alert
    if settings.ENABLE_SLACK_ALERTS and settings.SLACK_WEBHOOK_URL:
        # Mocking external API call
        logger.info(f"SLACK ALERT: Sent warning for {finding.entity_value} (Score: {finding.risk_score:.1f})")
        
        log_entry = AlertLog(
            finding_id=finding.id,
            channel="slack",
            status="sent"
        )
        repository.create_alert_log(log_entry)

    # Email Alert
    if settings.ENABLE_EMAIL_ALERTS and settings.SMTP_HOST:
        # Mocking external API call
        logger.info(f"EMAIL ALERT: Sent to admins for {finding.entity_value}")
        
        log_entry = AlertLog(
            finding_id=finding.id,
            channel="email",
            status="sent"
        )
        repository.create_alert_log(log_entry)
