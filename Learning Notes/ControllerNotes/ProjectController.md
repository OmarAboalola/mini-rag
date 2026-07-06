# ProjectController.py

---

## Comment 1

### 📝 Comment

```python
# inherit all shared functions from BaseController
```

### 💻 Code

```python
class ProjectController(BaseController):

    def __init__(self):
        super().__init__()
```

---

## Comment 2

### 📝 Comment

```python
# build the project's folder path
```

### 💻 Code

```python
project_dir = os.path.join(
    self.files_dir,
    project_id
)
```

---

## Comment 3

### 📝 Comment

```python
# create the folder if it doesn't exist
```

### 💻 Code

```python
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
```

---

## Comment 4

### 📝 Comment

```python
# return the project folder path
```

### 💻 Code

```python
return project_dir
```