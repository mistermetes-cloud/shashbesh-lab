# Experimental methodology / Методология

## RU — воспроизводимый протокол

До запуска фиксировать experiment_id, гипотезу, benchmark/version, exam/learning,
язык/версию правил, Core artifact SHA256, rulePolicy, action schema, observation
schema, участников/стороны 2–4, seed schedule, model/version, prompts, decoding
параметры, инструменты, лимиты времени/попыток/токенов и критерии исключения.
Внешние модели могут быть недетерминированными даже при одинаковом seed:
детерминизм Core не означает детерминизм модели. Хранить точные ответы и действия
для воспроизведения траектории; повторный вызов модели — новый эксперимент.

Разделять public training, development и private test fixtures по seed/семействам
состояний, исключать дубликаты state hashes. Для сравнения стратегий использовать
парные seed schedules и перестановки сторон; для 3/4 игроков учитывать состав
соперников и seat advantage. Бюджет и baseline одинаковы. Не запускать массовые
эксперименты на этапе архитектуры. Проспективно определить остановку серии.

Отдельные leaderboard cohorts: Strategy/Rules × Exam/Learning × язык × player
count × Core/policy × benchmark version × resource tier. Для Strategy публиковать
win/draw/unfinished, latency p50/p95, cost, timeout/error rate; неопределённая
партия не считается ничьей. Rules: first-attempt validity, categories, protocol
failures, timeouts; denominator включает все выданные scored tasks с объявленной
политикой истечения. Learning: success@k, attempts-to-valid, first error,
повтор ошибки, latency и стоимость до исправления. Неверный ответ после feedback
не превращает предыдущую неверную попытку в правильную.

Multi-player leaderboard: начать с win rate + доверительные интервалы по серии
и числу матчей; не переносить двухигровой Elo без модели составов/сторон.
Bootstrap делать по матчу/seed block, не по зависимым действиям. Публиковать размер
выборки, неопределённость, стратификацию и статус provisional для малых выборок.
Рейтинги разной policy/версии Core не сравниваются напрямую.

Сохранять manifest, входные task bytes, версии, даты, agent declaration,
каждую попытку/ошибку/feedback, accepted action, Core event seq/head hash,
seed/RNG counter (private), winner, replay checksum, runtime/resource metrics.
Raw model response может содержать персональные данные: доступ ограничен,
публичный экспорт проходит редактирование, хранение сроками и consent.
Объявленные provider/model сведения самодекларированы, если нет аттестации.

## EN — comparisons and evidence

Preregister hypotheses, cohorts, budgets, prompts, model/rules versions and
exclusion rules. Freeze seed schedules, rotate seats and control opponent
composition. Separate training/development/private tests; hash states to detect
leakage. Reproduce Core trajectories from exact actions; stochastic external
inference is not promised reproducible by seed alone.

Keep Strategy, Rules, Exam, Learning, language, player count and resource tiers
in separate rankings. Report sample sizes, uncertainty, timeout/error rates and
unfinished outcomes. Use match-level uncertainty, not independent-move claims.
Persist complete private provenance and publish only reviewed, consented data.
Agent capabilities and claimed model identity are not independently attested
by this architecture prototype.
