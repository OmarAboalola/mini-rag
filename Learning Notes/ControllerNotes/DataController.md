# DataController.py

---

## Comment 1

### 📝 Comment

```python
# class DataController extends BaseController
```

### 💻 Code

```python
class DataController(BaseController):
```

---

## Comment 2

### 📝 Comment

```python
# convert MB to bytes
```

### 💻 Code

```python
self.size_scale = 1048576
```

---

## Comment 3

### 📝 Comment

```python
# check if the uploaded file type is allowed
```

### 💻 Code

```python
if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
    return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
```

---

## Comment 4

### 📝 Comment

```python
# get the file size if it wasn't provided
```

### 💻 Code

```python
file_size = file.size
if file_size is None:
    current_position = file.file.tell()
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(current_position)
```

---

## Comment 5

### 📝 Comment

```python
# make sure the file doesn't exceed the max allowed size
```

### 💻 Code

```python
if file_size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
    return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
```

---

## Comment 6

### 📝 Comment

```python
# generate a random key for the uploaded file
```

### 💻 Code

```python
random_key = self.generate_random_string()
```

---

## Comment 7

### 📝 Comment

```python
# get the project's folder path
```

### 💻 Code

```python
project_path = ProjectController().get_project_path(
    project_id=project_id
)
```

---

## Comment 8

### 📝 Comment

```python
# remove unsupported characters from the file name
```

### 💻 Code

```python
cleaned_file_name = self.get_clean_file_name(
    orig_file_name=orig_file_name
)
```

---

## Comment 9

### 📝 Comment

```python
# create the new file path using the random key
```

### 💻 Code

```python
new_file_path = os.path.join(
    project_path,
    random_key + "_" + cleaned_file_name
)
```

---

## Comment 10

### 📝 Comment

```python
# regenerate the key if another file already has the same name
```

### 💻 Code

```python
while os.path.exists(new_file_path):
    random_key = self.generate_random_string()
    new_file_path = os.path.join(
        project_path,
        random_key + "_" + cleaned_file_name
    )
```

---

## Comment 11

### 📝 Comment

```python
# remove any special characters except letters, numbers, underscore and dot
```

### 💻 Code

```python
cleaned_file_name = re.sub(
    r'[^\w.]',
    '',
    orig_file_name.strip()
)
```

---

## Comment 12

### 📝 Comment

```python
# replace spaces with underscores
```

### 💻 Code

```python
cleaned_file_name = cleaned_file_name.replace(" ", "_")
```