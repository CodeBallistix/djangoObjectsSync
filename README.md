# signalsTest
Just testing the Signals functionality of Django to create an OpLog

Used the Signals module of python.

- The `signals.py` file in the polls app is imported in the AppConfig Class in the ready function.
- The logging configuration has been changed. check `settings.py` for Logging configuration
- major code in `signalsTest/settings.py`, `polls/models.py`, `polls/signals.py`
- verified using `python3 manage.py shell`
- the oplog contains the operation type which can be SAVE or DELETE
- the oplog contains the epoch time in seconds and milliseconds which may be used to check where to start the ingestion again


Run the Following Commands in django shell after all migrations have been made to verify functionality.
```python
from polls.models import Choice, Question
from django.utils  import timezone
q = Question(question_text="What's new?", pub_date=timezone.now())
q.save()
q.choice_set.create(choice_text='Nothing',votes=0)
c=q.choice_set.create(choice_text='sky',votes=0)
c.delete()
c.save()
```

The following output will be created and similar logs will be appended to the file at `logs/oplog.log`.

```
1698395500.971553 SAVE [{"model": "polls.question", "pk": 1, "fields": {"id": "a3f4729c-b3c2-4264-82a6-8ef7abeaec96", "question_text": "What's new?", "pub_date": "2023-10-27T08:31:40.182Z"}}]
1698395542.826431 SAVE [{"model": "polls.choice", "pk": 1, "fields": {"id": "d6d2c0a0-6dfa-4515-875e-f1edfd3dbf01", "question": "a3f4729c-b3c2-4264-82a6-8ef7abeaec96", "choice_text": "Nothing", "votes": 0}}]
1698395568.857164 SAVE [{"model": "polls.choice", "pk": 2, "fields": {"id": "d8e48b8d-9ccb-4728-b90c-2833592b6fd2", "question": "a3f4729c-b3c2-4264-82a6-8ef7abeaec96", "choice_text": "sky", "votes": 0}}]
1698395573.036682 DELETE [{"model": "polls.choice", "pk": 2, "fields": {"id": "d8e48b8d-9ccb-4728-b90c-2833592b6fd2", "question": "a3f4729c-b3c2-4264-82a6-8ef7abeaec96", "choice_text": "sky", "votes": 0}}]
1698395577.627465 SAVE [{"model": "polls.choice", "pk": 3, "fields": {"id": "d8e48b8d-9ccb-4728-b90c-2833592b6fd2", "question": "a3f4729c-b3c2-4264-82a6-8ef7abeaec96", "choice_text": "sky", "votes": 0}}]

```
