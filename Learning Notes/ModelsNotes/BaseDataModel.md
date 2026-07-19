# BaseDataModel.py

---

## Comment 1

### 📝 Comment

```python
# intialise db client so that any child can use it
# without having to create a new instance
```

### 💻 Code

```python
class BaseDataModel:
    def __init__(self, db_client):
        self.db_client = db_client
        self.app_settings = get_settings()
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