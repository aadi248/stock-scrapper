import logging

logging.basicConfig(
    filename='news_monitor.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('NewsMonitor')

def log_article(company, title, url, timestamp, sentiment):
    msg = f"{company} | {sentiment.upper()} | {timestamp} | {title} | {url}"
    logger.info(msg)