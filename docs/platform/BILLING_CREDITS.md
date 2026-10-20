# Usage, quotas and credits / Использование, квоты и кредиты

## RU — учёт до оплаты

На первом этапе только измерение и бесплатные лимиты; платежи, цены и внешние
billing providers не подключаются. Внешний model inference оплачивает его
владелец: платформенные credits не обозначают provider tokens. Usage включает
Core CPU/wall, decisions, attempts, replay jobs/bytes, storage и сетевой объём;
сохраняются billable policy version и источник измерения. Приблизительный RSS
не выдаётся за точное облачное потребление. Статистика usage не задаёт тариф.

План данных новой базы: org_accounts; quota_policies(version, limits);
usage_events(id, org, match/task, meter, integer_quantity, unit, timestamp);
reservations(id, org, max_units, expires, task_id);
ledger(id, org, reservation, entry_type, signed_integer_units, settlement_key).
Append-only ledger: grant/reserve/settle/release/refund, без float и удаления
истории. Проводки и доступный баланс меняются в одной транзакционной authority;
D1 analytics может отставать. Credits никогда не списываются через KV eventual
consistency или только браузерный счётчик.

Перед задачей атомарно резервировать верхнюю границу с проверкой quota/balance.
Сдача результата: settle фактическое разрешённое использование и release остатка.
Duplicate request/queue delivery не создаёт второе списание (unique settlement).
Timeout/crash: reconciler однократно освобождает/урегулирует reservation по
публичной policy. Ошибки платформы не списываются; пользовательские неверные
попытки учитываются только по заранее объявленной policy. Retry не маскирует
новую попытку и не тарифицируется дважды как прежняя.

Показывать разработчику бесплатные квоты, расход и единицы RU/EN. Уведомление
перед тяжёлым Replay, предсказуемый max budget, 429 + Retry-After при исчерпании.
Разделить research outcomes и коммерческие entitlements; оплата не улучшает
score. План на платные credits — спецификация, не обещание подключённой оплаты.

## EN — auditable accounting

Start with usage measurement and free quotas. No payments are integrated.
Measure named units with versioned policies; platform credits are distinct from
model-provider billing. Use integer append-only ledger entries and atomic
reservation/settlement/release. Deduplicate delivery and retry by unique keys.
Reconcile crashes and apply an explicit refund/error policy. Never derive
balances from eventual caches or client state. Price and payment integration
require a later product/security decision.
