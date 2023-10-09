import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_DOC_URL
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    whats_new_url = urljoin(MAIN_DOC_URL, "whatsnew/")

    response = get_response(session, whats_new_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features="lxml")

    main_div = find_tag(soup, "section", attrs={"id": "what-s-new-in-python"})
    div_with_ul = find_tag(main_div, "div", attrs={"class": "toctree-wrapper"})
    sections_by_python = div_with_ul.find_all(
        "li", attrs={"class": "toctree-l1"})

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, "a")
        href = version_a_tag["href"]
        version_link = urljoin(whats_new_url, href)

        response = get_response(session, version_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, features="lxml")
        h1 = find_tag(soup, "h1")
        dl = find_tag(soup, "dl")
        dl_text = dl.text.replace("\n", " ")
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features="lxml")
    sidebar = find_tag(soup, "div", {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all("ul")

    for ul in ul_tags:
        if "All versions" in ul.text:
            a_tags = ul.find_all("a")
            break
        else:
            raise Exception("Ничего не нашлось")

    # Шаблон для поиска версии и статуса:
    pattern = r"Python (?P<version>\d\.\d+) \((?P<status>.*)\)"

    for a_tag in a_tags:
        link = a_tag["href"]
        text_match = re.search(pattern, a_tag.text)

        if text_match is not None:
            version = text_match.group("version")
            status = text_match.group("status")
        else:
            version = a_tag.text
            status = ""

        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, "download.html")

    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features="lxml")
    main_tag = find_tag(soup, "table")
    pdf_a4_tag = find_tag(main_tag, "a",
                          {"href": re.compile(r".+pdf-a4\.zip$")})
    pdf_a4_link = pdf_a4_tag["href"]
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split("/")[-1]

    downloads_dir = BASE_DIR / "downloads"
    downloads_dir.mkdir(exist_ok=True)

    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, "wb") as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):

    output = [['Статус', 'Количество']]

    response = get_response(session, PEP_DOC_URL)
    if response is None:
        return

    # Создание "супа".
    soup = BeautifulSoup(response.text, features="lxml")
    # отбираем таблицы из раздела "по-категориям"
    tables = soup.find_all('section', attrs={'id': 'index-by-category'})

    # список для хранения результатов обработки строк
    results = []
    for tab_space in tables:
        # выделяем все табличные части
        lines = tab_space.find_all('tbody')
        # разбиваем на строки табличную часть
        for line in lines:
            result_lines = line.find_all('tr')
            # разбираем каждую строку
            for item in result_lines:
                type_status = item.find('abbr')
                type_status = type_status.text if type_status else ''
                link = find_tag(item, 'a')['href']
                # сохраняем результаты анализа строки
                results.append([type_status, PEP_DOC_URL + link])

    # создаем список для подсчета PEP в каждом статусе
    account = []

    # анализ содержимого карточки
    for pep_item in results:
        # загрузка данных карточки
        response = get_response(session, pep_item[1])
        if response is None:
            return

        # Создание "супа".
        soup = BeautifulSoup(response.text, features="lxml")
        # получение статуса из карточки
        status_in_card = soup.find('abbr').text
        # и добавление этого статуса в исходный список
        pep_item.append(status_in_card)

        # раворачиваем обозначение статуса в списке в текстовый вид
        if len(pep_item[0]) == 2:
            status_in_list = EXPECTED_STATUS[pep_item[0][1]]
        else:
            # если в списке в первой колонке только один символ
            # то есть указан только тип
            status_in_list = EXPECTED_STATUS['']

        # pep_item.append(status_in_list)
        # проверяем соответствие статусов из списка и из карточки
        if status_in_card not in status_in_list:
            pep_item.append(False)
            logging.info(f'Несовпадающие статусы:\n'
                         f'{pep_item[1]}\n'
                         f'Статус в карточке: {status_in_card}\n'
                         f'Ожидаемый статус: {status_in_list}')
        # Добавляем в список для подсчета стаус из карточки
        account.append(status_in_card)

    # составляем множество статусов
    account_set = set(account[:])

    # подсчет количества статусов
    for item in account_set:
        quantity = account.count(item)
        output.append([item, quantity])
    # Добавляем итоговоую строку
    output.append(['Total', len(account)])

    return output


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():

    # Запускаем функцию с конфигурацией логов.
    configure_logging()

    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')

    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())

    # Считывание аргументов из командной строки.
    args = arg_parser.parse_args()

    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')

    # Создание кеширующей сессии.
    session = requests_cache.CachedSession()
    # Если был передан ключ '--clear-cache', то args.clear_cache == True.
    if args.clear_cache:
        # Очистка кеша.
        session.cache.clear()

    # Получение из аргументов командной строки нужного режима работы.
    parser_mode = args.mode

    # Поиск и вызов нужной функции по ключу словаря.
    results = MODE_TO_FUNCTION[parser_mode](session)

    # Если из функции вернулись какие-то результаты,
    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)

    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
