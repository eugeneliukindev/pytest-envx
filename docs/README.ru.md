
[![PyPI version](https://badge.fury.io/py/pytest-envx.svg)](https://badge.fury.io/py/pytest-envx)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-envx.svg)](https://pypi.org/project/pytest-envx/)
[![codecov](https://codecov.io/gh/eugeneliukindev/pytest-envx/branch/master/graph/badge.svg?token=JRCQR1PFZ0)](https://codecov.io/gh/eugeneliukindev/pytest-envx)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE.txt)

# 🔧 pytest-envx

**pytest-envx** — это мощный и удобный плагин для [pytest](https://pytest.org), позволяющий удобно управлять переменными окружения из конфигурационных файлов `pyproject.toml`, `pytest.ini`

---

## 🚀 Возможности

- ✔️ Интерполяция переменных окружения через шаблоны
- ✔️ Загрузка переменных из `.env`
- ✔️ Совместимость с `pyproject.toml` и `pytest.ini`
- ✔️ Простота настройки и использования
- ✔️ Гибкая поддержка перезаписи и порядка загрузки

---

## ⚡️ Установка

```bash
pip install pytest-envx
```

---

## 📦 Быстрый старт

Создайте конфигурационный файл `pyproject.toml` ⚙️ или `pytest.ini` ⚙️
По умолчанию `pytest` ставит в приоритет `pytest.ini` ⚙️

### ✅ Пример 1: Простая переменная

<table>
  <tr>
    <th>pyproject.toml ⚙️</th>
    <th>pytest.ini ⚙️</th>
  </tr>
  <tr>
    <td>
      <pre lang="toml"><code>[tool.pytest.ini_options]
env = [
    "HELLO='WORLD'"
]</code></pre>
    </td>
    <td>
      <pre lang="ini"><code>[pytest]
env =
    HELLO="WORLD"</code></pre>
    </td>
  </tr>
</table>

**`test_example.py`** 🐍:

```python
import os


def test_env_var():
    assert os.getenv("HELLO") == "WORLD"
```

---



### ✅ Пример 2: Загрузка из `.env` 🔐 файлов с перегрузкой

<table>
  <tr>
    <th>.env-template 🔐</th>
    <th>.env 🔐</th>
  </tr>
  <tr>
    <td>
      <pre lang="dotenv">
NAME=ALICE
LASTNAME=BAILER
      </pre>
    </td>
    <td>
      <pre lang="dotenv">
NAME=BOB
      </pre>
    </td>
  </tr>
</table>

<table>
  <tr>
    <th>pyproject.toml ⚙️</th>
    <th>pytest.ini ⚙️</th>
  </tr>
  <tr>
    <td>
      <pre lang="toml">
[tool.pytest.ini_options]
envx_metadata = { paths_to_load = [".env-template", ".env"], override_load = true }
env = [
    "GREETING='Hello'"
]
      </pre>
    </td>
    <td>
      <pre lang="ini">
[pytest]
envx_metadata = {"paths_to_load": [".env-template", ".env"], "override_load": True}
env =
    GREETING="Hello"
      </pre>
    </td>
  </tr>
</table>

**`test_env_load.py`** 🐍:

```python
import os


def test_env_loading():
    assert os.getenv("NAME") == "BOB"
    assert os.getenv("LASTNAME") == "BAILER"
    assert os.getenv("GREETING") == "Hello"
```

---

### ✅ Пример 3: Загрузка из `.env` 🔐 файлов без перегрузки

<table>
  <tr>
    <th>.env.default 🔐</th>
    <th>.env.dev 🔐</th>
  </tr>
  <tr>
    <td>
      <pre lang="dotenv">
MODE=default
      </pre>
    </td>
    <td>
      <pre lang="dotenv">
MODE=development
LEVEL=DEV
      </pre>
    </td>
  </tr>
</table>

<table>
  <tr>
    <th>pyproject.toml ⚙️</th>
    <th>pytest.ini ⚙️</th>
  </tr>
  <tr>
    <td>
      <pre lang="toml">
[tool.pytest.ini_options]
envx_metadata = { paths_to_load = [".env.default", ".env.dev"], override_load = false }
      </pre>
    </td>
    <td>
      <pre lang="ini">
[pytest]
envx_metadata = {"paths_to_load": [".env.default", ".env.dev"], "override_load": False}
      </pre>
    </td>
  </tr>
</table>

**`test_priority.py`** 🐍:

```python
import os


def test_env_priority():
    assert os.getenv("MODE") == "default"
    assert os.getenv("LEVEL") == "DEV"
```

### ✅ Пример 4: Интерполяция переменных

<table>
  <tr>
    <th>.env 🔐</th>
  </tr>
  <tr>
    <td>
      <pre lang="dotenv">
USER=john
PASS=secret
HOST=db.local
PORT=5432
      </pre>
    </td>
  </tr>
</table>

<table>
  <tr>
    <th>pyproject.toml ⚙️</th>
    <th>pytest.ini ⚙️</th>
  </tr>
  <tr>
    <td>
      <pre lang="toml">
[tool.pytest.ini_options]
envx_metadata = { paths_to_interpolate = [".env"] }
env = [
    "DB_URL_WITH_INTERPOLATION='postgresql://{%USER%}:{%PASS%}@{%HOST%}:{%PORT%}/app'",
    "WITHOUT_INTERPOLATION={'value': '{%USER%}', 'interpolate': False}",
    "NOT_FOUND='{%NOT_FOUND%}'"
]
      </pre>
    </td>
    <td>
      <pre lang="ini">
[pytest]
envx_metadata = {"paths_to_interpolate": [".env"]}
env =
    DB_URL_WITH_INTERPOLATION="postgresql://{%USER%}:{%PASS%}@{%HOST%}:{%PORT%}/app"
    WITHOUT_INTERPOLATION={"value": "{%USER%}", "interpolate": False}
    NOT_FOUND = "{%NOT_FOUND%}"
      </pre>
    </td>
  </tr>
</table>

**`test_interpolation.py`** 🐍:

```python
import os


def test_interpolated_value():
    assert os.getenv("DB_URL_WITH_INTERPOLATION") == "postgresql://john:secret@db.local:5432/app"
    assert os.getenv("WITHOUT_INTERPOLATION") == "{%USER%}"
    assert os.getenv("NOT_FOUND") == "{%NOT_FOUND%}"
    assert os.getenv("USER") != "john"
    assert os.getenv("PASS") != "secret"
    assert os.getenv("HOST") != "db.local"
    assert os.getenv("PORT") != "5432"
```

---

## ⚙️ envx_metadata

| Параметр               | Тип     | Описание |
|------------------------|---------|----------|
| `paths_to_load`        | список  | Пути к `.env` файлам для загрузки переменных (будут загружены в порядке объявления) |
| `override_load`        | (bool, default=True)    | Перезаписывать установленные переменные при загрузке |
| `paths_to_interpolate` | список  | Пути к файлам для интерполяции значений |
| `override_interpolate` | (bool, default=True)     | Перезаписывать установленные переменные при интерполяции |

---

## 📄 Лицензия

[MIT](../LICENSE.txt)
