import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup


ANNOUNCEMENT_URL = "https://www.scjsjds.cn/web/guest/ssgg"
STATE_FILE = Path(__file__).with_name("monitor_state.json")
CHECK_INTERVAL_SECONDS = 300
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

# 这些关键词对应“成绩出来了”的业务含义。
KEYWORDS = [
    "评审结果",
    "结果名单",
    "获奖",
    "获奖名单",
    "获奖公示",
    "获奖公告",
    "名单公示",
    "名单公告",
]


def fetch_latest_announcement():
    request = urllib.request.Request(ANNOUNCEMENT_URL, headers=REQUEST_HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8", errors="ignore")

    soup = BeautifulSoup(html, "html.parser")
    latest_item = soup.select_one("li.article-item")
    if latest_item is None:
        raise RuntimeError("未找到公告列表，页面结构可能发生变化。")

    link = latest_item.select_one("a[href]")
    date_node = latest_item.select_one("span")
    if link is None:
        raise RuntimeError("未找到最新公告链接，页面结构可能发生变化。")

    title = " ".join(link.get_text(strip=True).split())
    href = urllib.parse.urljoin(ANNOUNCEMENT_URL, link["href"])
    publish_date = date_node.get_text(strip=True) if date_node else ""

    return {
        "title": title,
        "url": href,
        "publish_date": publish_date,
    }


def is_result_announcement(title):
    return any(keyword in title for keyword in KEYWORDS)


def load_state():
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state):
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def show_popup(message, title="四川省赛通知监控"):
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
    except Exception:
        print(f"[弹窗失败] {title}: {message}")


def print_status(prefix, announcement):
    print(
        f"{prefix} {announcement['publish_date']} | "
        f"{announcement['title']} | {announcement['url']}",
        flush=True,
    )


def monitor_forever():
    print(f"开始监控: {ANNOUNCEMENT_URL}", flush=True)
    print(f"检查间隔: {CHECK_INTERVAL_SECONDS} 秒", flush=True)
    print(f"状态文件: {STATE_FILE}", flush=True)

    while True:
        try:
            latest = fetch_latest_announcement()
            state = load_state()
            previous_url = state.get("latest_url")

            if not previous_url:
                save_state(
                    {
                        "latest_url": latest["url"],
                        "latest_title": latest["title"],
                        "latest_publish_date": latest["publish_date"],
                    }
                )
                print_status("[首次记录]", latest)
            elif latest["url"] != previous_url:
                save_state(
                    {
                        "latest_url": latest["url"],
                        "latest_title": latest["title"],
                        "latest_publish_date": latest["publish_date"],
                    }
                )
                print_status("[发现新公告]", latest)

                if is_result_announcement(latest["title"]):
                    show_popup("成绩出来了")
                    print("[已触发弹窗] 成绩出来了", flush=True)
                else:
                    print("[未触发弹窗] 新公告不属于成绩类通知", flush=True)
            else:
                print_status("[无变化]", latest)
        except KeyboardInterrupt:
            print("监控已停止。", flush=True)
            raise
        except Exception as exc:
            print(f"[检查失败] {exc}", flush=True)

        time.sleep(CHECK_INTERVAL_SECONDS)


def run_once():
    latest = fetch_latest_announcement()
    print_status("[当前最新公告]", latest)
    print(
        "[成绩类通知]"
        if is_result_announcement(latest["title"])
        else "[非成绩类通知]",
        flush=True,
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
    else:
        monitor_forever()
