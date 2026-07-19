# ProjectModel.py

---

## Comment 1

### 📝 Comment

```python
# the logic of the project db table is handled here.
# This class is responsible for all the db operations
# related to the project table
```

### 💻 Code

```python
class ProjectModel(BaseDataModel):
```

---

## Comment 2

### 📝 Comment

```python
# connect to the project collection(table) in the database
```

### 💻 Code

```python
self.collection = self.db_client[
    COLLECTION_PROJECT_NAME.value
]
```

---

## Comment 3

### 📝 Comment

```python
# do opertaions on the collection
```

### 💻 Code

```python
# CRUD methods below
```

---

## Comment 4

### 📝 Comment

```python
# insertion function
```

### 💻 Code

```python
async def create_project(self, project: Project):
```

---

## Comment 5

### 📝 Comment

```python
# async function to insert a project into the collection
```

### 💻 Code

```python
async def create_project(self, project: Project):
```

---

## Comment 6

### 📝 Comment

```python
# we created a project object in the db_schemes.py file
# (to mentain the data shape) and we are using it here
# to insert a project into the collection
```

### 💻 Code

```python
async def create_project(self, project: Project):
```

---

## Comment 7

### 📝 Comment

```python
# used motor (async mongo db driver) to insert the project into the collection
```

### 💻 Code

```python
result = await self.collection.insert_one(
    project.dict()
)
```

---

## Comment 8

### 📝 Comment

```python
# convert the project object to a dictionary
# and insert it into the collection
```

### 💻 Code

```python
project.dict()
```

---

## Comment 9

### 📝 Comment

```python
# async function to get a project by its id if not found create it .
```

### 💻 Code

```python
async def get_project_or_create_one(
    self,
    project_id: str
):
```

---

## Comment 10

### 📝 Comment

```python
# convert from dict (returning from db) to Project object and return it
```

### 💻 Code

```python
return Project(**record)
```

---

## Comment 11

### 📝 Comment

```python
# never use get_all without pagination
```

### 💻 Code

```python
async def get_all_projects(
    self,
    page: int,
    page_size: int
):
```

---

## Comment 12

### 📝 Comment

```python
# count all the documents in the collection
```

### 💻 Code

```python
total_documets = await self.collection.count_documents({})
```

---

## Comment 13

### 📝 Comment

```python
# calculate the total number of pages
```

### 💻 Code

```python
total_pages = (total_documets // page_size)
```

---

## Comment 14

### 📝 Comment

```python
# round up the total pages if there are remaining documents
```

### 💻 Code

```python
if total_documets % page_size > 0:
    total_pages += 1
```

---

## Comment 15

### 📝 Comment

```python
# skip the documents of the previous pages and limit the number of documents to the page size
# does not return the data , it returns a cursor (pointer) object which can be iterated to get the data
```

### 💻 Code

```python
cursor = (
    self.collection.find()
    .skip((page - 1) * page_size)
    .limit(page_size)
)
```

---

## Comment 16

### 📝 Comment

```python
# cursor is an async iterator so we need to use async for to iterate over it
```

### 💻 Code

```python
async for document in cursor:
```

---

## Comment 17

### 📝 Comment

```python
# convert from dict to Project object(there for it needs an id (mandatory)) and append it to the list
```

### 💻 Code

```python
projects.append(Project(**document))
```

---