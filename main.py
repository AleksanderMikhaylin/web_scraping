import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import re
import json

headers_generator = Headers(os='win', browser='Yandex')

params = {
        'text': 'python',
        'area': [1,2]
}
# https://hh.ru/search/vacancy?text=python&area=1&area=2
response = requests.get('https://hh.ru/search/vacancy/', headers=headers_generator.generate(), params=params)
if not response.status_code == 200:
    print('Ошибка получения информации')
    exit()

main_html_data = response.text
main_soup = BeautifulSoup(main_html_data, 'lxml')
vacancy_list = main_soup.find_all('div', class_='serp-item')

vacancy_data = []
for vacancy_item in vacancy_list:
    vacancy_info_tag = vacancy_item.find('a', class_='serp-item__title')

    if vacancy_info_tag is None:
        print(f'Не найдена ссылка для получения информации по вакансии {vacancy_info_tag.text}')
        continue

    response = requests.get(vacancy_info_tag['href'], headers=headers_generator.generate())
    if not response.status_code == 200:
        print(f'Ошибка получения информации по вакансии {vacancy_info_tag.text}')
        continue

    vacancy_html_data = response.text
    vacancy_soup = BeautifulSoup(vacancy_html_data, 'lxml')

    find_words = False
    vacancy_tag = vacancy_soup.find('div', {'class': 'g-user-content', 'data-qa': 'vacancy-description'})
    if not vacancy_tag is None:
        vacancy_tag_span = vacancy_tag.find_all('p')
        for el in vacancy_tag_span:
            if len(re.findall(r'Django|Flask', el.text, re.I)) > 0:
                find_words = True
                break

    if not find_words:
        continue

    company = ''
    vacancy_tag = vacancy_item.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
    if not vacancy_tag is None:
        company = ' '.join(re.findall(r'\w+', vacancy_tag.text, re.I))

    city = ''
    vacancy_tag = vacancy_soup.find('p', {'data-qa': 'vacancy-view-location'})
    if not vacancy_tag is None:
        city = ' '.join(re.findall(r'\w+', vacancy_tag.text, re.I))

    salary = ''
    vacancy_tag = vacancy_soup.find('div', {'data-qa': 'vacancy-salary'})
    if not vacancy_tag is None:
        salary = ' '.join(re.findall(r'\w+', vacancy_tag.text, re.I))
        salary_in_USD = vacancy_tag.text.find('$') > 0

    vacancy_dict = {
        'href': vacancy_info_tag['href'],
        'salary': salary,
        'salary_in_USD': salary_in_USD,
        'company': company,
        'city': city
    }

    vacancy_data.append(vacancy_dict)

with open("vacancy.json", 'w', encoding='utf-8') as f:
	json.dump(vacancy_data, f, ensure_ascii = False, indent = 2)
