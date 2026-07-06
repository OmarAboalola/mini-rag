# BaseController.py

---

## Comment 1

### 📝 Comment

```python
# this file is used to define the base controller class
# that will be inherited by all other controllers in the application
```

### 💻 Code

```python
from helpers.config import get_settings, Settings
import os
import random
import string

class BaseController:

    def __init__(self):

        self.app_settings = get_settings()

        self.base_dir = os.path.dirname(
            os.path.dirname(__file__)
        )

        self.files_dir = os.path.join(
            self.base_dir,
            "assets/files"
        )

    def generate_random_string(self, length: int = 12):
        return ''.join(
            random.choices(
                string.ascii_lowercase + string.digits,
                k=length
            )
        )
```

---

## Comment 2

### 📝 Comment

```python
# load the project settings once
```

### 💻 Code

```python
self.app_settings = get_settings()
```

---

## Comment 3

### 📝 Comment

```python
# get the src folder path
```

### 💻 Code

```python
self.base_dir = os.path.dirname(
    os.path.dirname(__file__)
)
```

---

## Comment 4

### 📝 Comment

```python
# path to where uploaded files will be stored
```

### 💻 Code

```python
self.files_dir = os.path.join(
    self.base_dir,
    "assets/files"
)
```

---

## Comment 5

### 📝 Comment

```python
# generate a random file/folder name
```

### 💻 Code

```python
def generate_random_string(self, length: int = 12):
    return ''.join(
        random.choices(
            string.ascii_lowercase + string.digits,
            k=length
        )
    )
```