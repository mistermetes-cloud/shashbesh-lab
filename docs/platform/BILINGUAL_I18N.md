# Bilingual i18n / Двуязычность

## RU — обязательный контракт

Research UI и документация разработчика поддерживают `ru` и `en` на одинаковом
уровне. Маршруты `/ru/…` и `/en/…`; явный выбор сохраняется в профиле или локально.
Первый выбор — Accept-Language, затем en; неизвестный язык не создаёт ошибку
протокола. Переключение сохраняет match_id, режим, cursor и выделенную фишку.
Язык публичной игры независимо управляется её проектом.

Все надписи — стабильные ключи: `dice.roll`, `agent.invalid_action`,
`benchmark.exam`, `billing.balance`. ICU-style plural/select для русского
one/few/many и английского one/other; формат дат UTC в API, локальный timezone
только при показе. Locale-aware числа, отсутствие конкатенации предложений.
Ошибки API возвращают code + безопасные params; клиент локализует сообщение.
Core IDs клеток, действия, хеши, имена событий и ключи JSON не переводятся.

Пример каталогов (проект, не изменение текущего Viewer):

| Key | ru | en |
|---|---|---|
| dice.roll | БРОСИТЬ КУБИКИ | ROLL DICE |
| agent.invalid_action | Недопустимое действие | Invalid action |
| benchmark.exam | Экзамен | Exam |
| benchmark.learning | Обучение | Learning |

Оба языка проверяются по одинаковому набору ключей и параметров; CI запрещает
пропуски, HTML в переводах и утечки сырых ошибок. Проверять длинные строки,
320–1920px, keyboard/touch, screen reader и aria-live статуса броска. Стабильность
поля важнее длины текста: текст переносится в фиксированных панелях.

Язык задачи — экспериментальный фактор. Rules benchmark фиксирует язык правил,
версию перевода и prompt hash; русский и английский результаты не объединяются
без заранее объявленного bilingual-протокола. Machine action schema одинакова.
Переводы правил проверяются человеком; перевод не меняет Core rulePolicy.

## EN — parity and research validity

Support ru/en equally in routes, navigation, help, errors, registration and
reports. Persist explicit preference; use Accept-Language only for the initial
choice. Keep Core identifiers and JSON keys invariant. API errors use stable
codes, not localized free text. Localize dates/numbers only in presentation.

Use matching catalog keys, plural forms and accessibility labels. Switching
language preserves game and Replay position. Test long labels without moving
the board. Fix the language, translation version and prompt hash per benchmark;
do not silently pool Russian and English rule-comprehension scores. UI
localization and bilingual editorial review are future implementation work.
