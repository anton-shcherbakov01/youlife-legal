# Уведомления о компонентах третьих лиц

Документ является неотъемлемой частью Лицензионного соглашения (`TERMS_OF_USE.md`),
пункт 12.2.

Игра использует перечисленные ниже компоненты. Полные тексты лицензий доступны по указанным
ссылкам. Ссылки вида `gradle/libs.versions.toml` указывают на файлы репозитория Игры — они
приведены для точности состава версий и не требуются для чтения настоящего документа.

## Библиотеки

| Компонент | Версия | Лицензия |
| --- | --- | --- |
| Kotlin, kotlinx.serialization (JetBrains) | 2.0.21 / 1.7.3 | Apache License 2.0 |
| AndroidX Core, Activity, Lifecycle, Navigation | см. `gradle/libs.versions.toml` | Apache License 2.0 |
| Jetpack Compose (UI, Foundation, Material 3, Material Icons) | Compose BOM 2024.11.00 | Apache License 2.0 |
| AndroidX WorkManager | 2.10.0 | Apache License 2.0 |
| AndroidX Graphics Path | транзитивная | Apache License 2.0 |
| Google ZXing Core | 3.5.3 | Apache License 2.0 |

Текст лицензии: Apache License 2.0 — <https://www.apache.org/licenses/LICENSE-2.0>.

## Проприетарные компоненты магазинов приложений

Эти компоненты распространяются не по открытой лицензии, а по соглашениям правообладателей,
и присутствуют только в сборке для соответствующего магазина.

**Сборка для RuStore:**

| Компонент | Версия | Лицензия |
| --- | --- | --- |
| `ru.rustore.sdk:pay` | 11.1.0 | Лицензионное соглашение RuStore SDK — <https://www.rustore.ru/help/sdk/> |
| `ru.rustore.sdk:core`, `:reactive`, `:analytics`, `:metrics`, `:userprofile`, `:installidentifier`, `:imaging` | транзитивные (10.5.x) | там же |
| `ru.ok.tracer:tracer-base`, `:tracer-platform`, `:tracer-manifest`, `:tracer-lite-commons`, `:tracer-lite-crash-report` | 1.4.0 | Tracer's License Agreement — <https://apptracer.ru/license/> |

**Сборка для Google Play:**

| Компонент | Версия | Лицензия |
| --- | --- | --- |
| Google Play Billing Library (`com.android.billingclient:billing`) | 9.1.0 | Условия использования Android Software Development Kit — <https://developer.android.com/studio/terms> |
| Google Play services (base, basement, tasks, location, places-placereport), Google Data Transport, Firebase Encoders | транзитивные | там же; Apache License 2.0 — для компонентов, распространяемых по ней |

Библиотека Google Play Billing подтягивает компонент `play-services-location`; Игра не
запрашивает разрешений на определение местоположения, и без такого разрешения компонент
доступа к местоположению не получает.

Какие технические сведения эти компоненты могут передавать операторам магазинов, описано
в пункте 4.6 Политики конфиденциальности (`PRIVACY_POLICY.md`).

## Шрифты

Шрифты эпох включены в Игру и распространяются по SIL Open Font License 1.1 —
<https://openfontlicense.org/open-font-license-official-text/>.

| Шрифт | Правообладатель |
| --- | --- |
| Forum | Denis Masharov |
| Cormorant Garamond | The Cormorant Project Authors |
| Alegreya | The Alegreya Project Authors |
| EB Garamond | The EB Garamond Project Authors |
| Old Standard TT | The Old Standard Project Authors |
| Playfair Display | The Playfair Display Project Authors |
| PT Serif | ParaType Ltd. |
| Manrope | The Manrope Project Authors |
| Unbounded | The Unbounded Project Authors |

## Данные

Очертания держав, рельеф и названия областей на картах Игры построены из данных Natural Earth
(<https://www.naturalearthdata.com>), находящихся в общественном достоянии, и переработаны
для Игры.

## Изображения и звук

Портреты, гербы, панорамы и иные изображения Игры созданы для Игры либо строятся её кодом.
Звуки синтезируются кодом Игры во время работы. Стоковые фотографии, иллюстрации и
звукозаписи третьих лиц не используются.
