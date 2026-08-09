from apscheduler.schedulers.background import BackgroundScheduler

from models.topic import Topic
from services.pipeline_service import process_topic


scheduler = BackgroundScheduler()


def autonomous_cycle(app):
    """Process the latest scored topic."""

    with app.app_context():
        topic = (
            Topic.query
            .filter_by(status="scored")
            .order_by(Topic.id.desc())
            .first()
        )

        if topic is None:
            print("[AUTONOMOUS] No scored topics available.")
            return

        print(f"[AUTONOMOUS] Processing topic {topic.id}: {topic.title}")

        try:
            result = process_topic(topic)

            print(
                f"[AUTONOMOUS] success={result['success']} "
                f"stage={result['stage']}"
            )

        except Exception as exc:
            print(f"[AUTONOMOUS] ERROR: {exc}")


def start_scheduler(app):
    """Start the autonomous scheduler."""

    if scheduler.running:
        print("[AUTONOMOUS] Scheduler already running.")
        return

    scheduler.add_job(
        lambda: autonomous_cycle(app),
        trigger="interval",
        minutes=10,
        id="autonomous_cycle",
        replace_existing=True,
    )

    scheduler.start()

    print("[AUTONOMOUS] Scheduler started.")
