import requests
import json
import argparse

NOTIFICATION_TEXT = [
    "Осталось менее полугода до указанной даты следующего обучения преподавателя {}.",
    "Меньше, чем через три месяца наступит указанная дата следующего обучения преподавателя {}. Необходимо организовать обучение и поменять даты а базе.",
    "Меньше, чем через 30 дней наступит (или уже наступила) указанная дата переобучения преподавателя {}! Необходимо организовать обучение и поменять даты а базе."
]

IMPORTANCE = {
    180: "0", # важность низкая
    90: "1", # важность нейтральная
    30: "2" # важность высокая
}

"""
delta -- число дней, которое используется для проверки сроков. В def check_training(self) модели Worker (models.py) рассчитывается
разница (current_delta) между текущей датой и той датой, в которую преподавателю необходимо пройти следующее обучение.
Если разница меньше или равно delta, до даты обучения осталось меньше delta дней, а значит нужно организовать прохождение переобучения преподавателем.
Когда даты последнего актуального и ближайшего следующего обучения будут изменены, скрипт не будет реагировать на преподавателя,
пока не подойдут новые сроки. Уведомления добавляются с помощью API и рассылаются на почту с помощью lifecycle hook AFTER_CREATE модели Notification.
"""

def get_workers(delta: int) -> list:
    """
    Принимает число delta,
    отправляет запрос к адресу API для проверки актуальности данных о сроках образования,
    возвращает список преподавателей.

    delta -- число дней для проверки сроков
    """
    response: requests.Response = requests.get(
        "http://127.0.0.1:8000/workersdb/workers/check/{}".format(delta)
    )

    json_body = response.content

    body = json.loads(json_body)

    print(body)

    return body


def create_notification(notification_data: object) -> requests.Response:
    """
    Принимает объект notification_data,
    отправляет запрос к адресу API для создания уведомлений,
    возвращает HTTP-Response.
    """
    response: requests.Response = requests.post(
        "http://127.0.0.1:8000/workersdb/workers/notifications/create",
        data=json.dumps(notification_data),
        headers={"Content-type": "application/json"}
    )
    return response


def get_notification_data(worker: object, importance: str) -> object:
    """
    Принимает оюъект worker и значение importance,
    возвращает объект notification_data с данными полей уведомления.
    """
    notification_data = {
        "worker": worker['id'],
        "importance": importance,
        "text": NOTIFICATION_TEXT[int(importance)].format(worker['personal_info']['surname'])
    }

    return notification_data


def main(delta: int) -> None:
    """
    Принимает число delta,
    получается список преподавателей workers с помощью get_workers,
    создаёт уведомления для всех преподавателей.

    delta -- число дней для проверки сроков
    """
    workers = get_workers(delta)
    for worker in workers:
        notification_data = get_notification_data(worker, IMPORTANCE[delta])
        response = create_notification(notification_data)


parser = argparse.ArgumentParser(description='Число дней для проверки сроков переподготовки')
parser.add_argument("--d", default=0, type=int, help="delta в днях. Регулярный запуск выполняется с параметрами 30, 90, 180 (в порядке убывания важности).")

args = parser.parse_args()

d = args.d

main(d)
