# Skeletor
Скелетор — заготовка для сервисов.

## Локальная разработка
Для разработки проекта понадобятся Docker Compose, [pre-commit](https://pre-commit.com), [Task](https://taskfile.dev).

1. Склонировать проект.
2. Установить пре-коммит хуки: `pre-commit install --install-hooks`.
3. Склонировать сабмодуль c миграциями БД: `task submodules`. Для обновления в будущем использовать эту же команду.
4. Из папки с проектом выполнить `docker compose up --wait`. Будут развернуты все сервисы проекты, выполнена миграция БД.

Тесты можно запустить командой `task test`.

При необходимости изменить порты, которые ведут с хоста в сервисы, создать файл `.env` и добавить в него нужные
значения (см. переменные в `docker-compose.yml`).

### Запуск приложения на хосте
Если есть необходимость запустить приложение или тесты не в контейнере, а на своей машине, можно использовать
утилиту [direnv](https://direnv.net), экспортировав с ее помощью переменные окружения для подключения c хоста к сервисам
в контейнерах (БД, брокер).

Рабочий пример файла `.envrc` для запуска тестов:
```shell
export DB__DSN=postgres://user:password@0.0.0.0:5432/skeletor_test
export BROKERS__SKELETOR__URL=amqp://user:password@0.0.0.0:5672/skeletor
```

## Конфигурация
Для изменения дефолтной конфигурации приложения или сервисов используются добавочные файлы `docker-compose.*.yml`
(где * можно заменить на override или любое другое слово).

Пример файла, переопределяющего переменные окружения сервиса `api`:
```yaml
# docker-compose.override.yml
version: "3"

services:
  api:
    environment:
      DEBUG: false
```

Подробнее о том, как это работает: https://docs.docker.com/compose/multiple-compose-files/merge/

## Линтеры
Линтеры запускаются пре-коммит хуком при каждом коммите. Отдельно от коммита можно использовать команды `task lint`
(для проверки без исправлений) и `task fix` (для внесения исправлений).

## Grafana
### Добавление метрик проекта
Проект содержит файл `dashboard-template.json`. Это шаблон дашборда Grafana. Чтобы добавить метрики сервиса,
нужно создать новый дашборд, импортировав его из этого файла согласно 
[документации](https://grafana.com/docs/grafana/v9.5/dashboards/manage-dashboards/#import-a-dashboard).

Чтобы экспортировать шаблон в случае внесения изменений, нужно выполнить несколько шагов:
1. Экспортировать JSON-шаблон согласно 
[документации](https://grafana.com/docs/grafana/v9.5/dashboards/manage-dashboards/#export-a-dashboard), выбрав опцию 
**Export for sharing externally**.
2. В загруженном файле установить значения полей **title** = `""` и **uid** = `null`, очистить значения переменных (
`__inputs.[n].value`.

Шаблон состоит из нескольких групп метрик:
* Kube resources (ресурсы Kubernetes)
* Intra services API (клиенты к API внешних сервисов)
* RMQ (очереди RabbitMQ)
* Database (база данных)
* API (API сервиса)
* Business (бизнес-метрики)

В группе Business нет панелей по умолчанию, сюда можно добавлять бизнес-метрики, специфичные для
сервиса.

В шаблоне есть переменные, которые используются для кастомизации дашборда под конкретный сервис. При импортировании 
дашборда Grafana попросит указать значение этих переменных (в документации они обозначены как metric prefixes).

* `kubenamespace` - неймспейс Kubernetes, в котором развернут сервис
* `service` - базовое имя сервиса (как правило, имя репозитория)
* `vhost` - виртуальный хост RabbitMQ, используемый сервисом
* `rmq_prefix` - префикс очередей сервиса
* `rmq_env` - окружение RabbitMQ (qa/stage/prod)

### Добавление алертов проекта
Для каждого проекта мы создаем 4 алерта, и привязываем их к соответствующей панели в дашборде проекта.

1. Слишком много 500-х ответов от API (панель `500`)
2. Слишком много соединений с виртуальных хостом RabbitMQ (панель `Connections (vhost)`)
3. Слишком много сообщений в очередях RabbitMQ (панель `Messages total (queues)`)
4. У очереди нет ни одного консюмера (панель `Consumers (queues)`)

Чтобы добавить алерт для нового сервиса, нужно:
1. Сделать копию существующего алерта.
2. Переименовать новый алерт.
3. В запросе для алерта соответствующим образом изменить запрос (query), сообщение (лейбл `message`), и привязку к панели (`Set dashboard and panel`).
4. Сохранить алерт.
