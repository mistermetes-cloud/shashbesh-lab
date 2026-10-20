# Rules Benchmark / Испытание понимания правил

## RU — что измеряется

Rules оценивает способность предложить допустимое полное Core-действие по
состоянию и версионированному тексту правил без списка допустимых действий.
Strategy оценивает выбор среди Core legalActions. Эти рейтинги не смешиваются.
Текст правил, перевод и Core rulePolicy фиксируются вместе; спорный перевод
не меняет oracle, а блокирует публикацию соответствующей серии до проверки.

Task строится allowlist-проекцией: геометрия, стороны/фишки, активный игрок,
текущие кубики, оставшиеся единицы действия, forced piece, extra-roll.
Не передавать serialized Core state, eventLog, seed/RNG counter, legalActions,
количество вариантов, лучший ход, hidden fixture name, validation trace или
будущий replay URL. Проверять весь вложенный payload, а не только верхний ключ.
Имена task_id/lease_id непрозрачны, не кодируют категорию/ответ. Полная геометрия
и публичные последствия прежних действий не считаются утечкой правил.

Core legalActions вычисляются **внутри** evaluator. Канонически точное
предложение должно совпасть с действием Core; Python не проверяет прыжок,
обязательное сбитие, выход из дома или финиш отдельными правилами. Применение
также выполняет Core. Для решения без допустимых действий задачу выбора не
создавать: существующий контроллер вызывает finishRoll по контракту Core,
фиксирует переход/бонус и ищет следующий decision. Отдельный task-type pass
в v1 не вводится. Current prototype starts at a Core-provided nonempty choice.

Exam: первая schema-valid, lease-valid игровая попытка фиксируется неизменно;
при неправильном действии trial закрывается. Ответ `invalid_action`, без
эталона или корректирующей подсказки. Транспортный retry возвращает receipt,
а не вторую попытку. Malformed JSON, stale task, expired lease — отдельные
protocol/availability outcomes; после deadline trial получает timeout, чтобы
его нельзя было бесконечно избегать неправильными envelopes.

Learning: после неправильной попытки Core-состояние и revision неизменны.
Возвращается тот же общий feedback, разрешается новый request_id; лимиты
попыток и времени объявляются заранее. Правильная попытка закрывает trial и
выполняет Core action. Хранятся все попытки и связи feedback → next proposal;
измеряется изменение поведения, а не только итоговый успех.

В локальном прототипе exam-failure заканчивает isolated trial, не назначает
победителя и не выдумывает следующий ход. В будущих полных матчах неверная
попытка завершает benchmark run как invalid/forfeit **на уровне испытания**,
с reason и last valid Core state; победа Core остаётся null, если Core её не
зафиксировал. Нельзя записывать административный forfeit как Core victory.

## EN — disclosure and outcomes

Rules tests action construction from public state plus fixed rules text.
Strategy tests action selection from an enumerated Core list. Only Core judges
legality. Use an allowlist observation; exclude answer counts, traces, seed,
private journal and alternate action payloads. Hidden test fixtures stay private
until the evaluation window closes.

Exam seals the first validly delivered game attempt, with generic feedback.
Learning allows declared bounded retries at unchanged state after errors and
records feedback response. Transport failures, stale leases and malformed
messages are separate outcomes; deadline expiry cannot disappear from metrics.
No-action rolls are settled by Core/controller without invented agent moves.
Administrative termination is not a game-rule victory.

## Coverage gates / Категории

Use original-Core fixtures for deployment, mandatory capture, corner jump,
obstruction, exact finish, 6+6/four units, 6+5, zero-action rolls, same-player
bonus and 2/3/4-player turn transitions. Fixtures record Core version/hash,
policy, verified state/event hash and expected oracle privately. Synthetic
near-finish fixtures must be labeled; do not mix them with natural match rates.

The local tests establish protocol/disclosure semantics on real Core choices.
A reviewed bilingual rules corpus, balanced hidden fixture bank and full
Rules tournament integration are roadmap work, not claimed delivered here.
