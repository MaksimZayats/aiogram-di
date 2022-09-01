# Aiogram DI

## Installation

* Latest version from GitHub
  ```
  pip install git+https://github.com/MaximZayats/aiogram-di
  ```

* From PyPi
  ```
  pip install -U aiogram-di
  ```

## Usage

* ### Initialization
  ```python
  from aiogram_di import DIMiddleware

  @dataclass
  class A:
      id: int

  dp.message.middleware(
      DIMiddleware(
          {
              A: lambda: A(id=1),
          }
      )
  )
  ```

* ### Usage
  ```python
  @dp.message()
  async def handler(
      message: Message,
      a: A,  # <- will be injected
  ) -> None:
    assert a.id == 1
  ```
