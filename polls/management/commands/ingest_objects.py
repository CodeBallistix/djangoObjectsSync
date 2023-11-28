from django.core.management.base import BaseCommand
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from polls.models import ProcessedFile
from rest_framework.parsers import JSONParser
from django.core import serializers
import os
import time
import traceback
import logging

logger = logging.getLogger()

def ingest_object( line):
    try:
        logger.debug(msg=f'ingest_object')
        s = line[line.find(' ')+1:]
        op = s[:s.find(' ')]
        data = serializers.deserialize('json', s[s.find(' ')+1:],)
        if op == 'SAVE':
            for obj in data:
                print(obj)
                obj.save()
                logger.info(msg=f'ingest_object SAVED Object ID {obj.object.id}')
        elif op == 'DELETE':
            for obj in data:
                o = obj.object.__class__.objects.get(id=obj.object.id)
                print(o)
                o.delete()
                logger.info(msg=f'ingest_object DELETE Object ID {obj.object.id}')
    except Exception as e:
        logger.error(msg=f'ingest_object {e} {line}')
        logger.error(msg=f'ingest_object ERROR {traceback.format_exc()}')

class ObjectIngestHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = file_path

    def on_modified(self, event):
        if event.src_path == self.file_path and event.event_type == 'modified':
            logger.info(msg=f'The Operational Log was modified.')
            logger.debug(msg=f'Starting Ingestion')
            self.ingest_objects()
            logger.debug(msg=f'Completed Ingestion')
    
    def on_created(self, event):
        if event.src_path == self.file_path:
            logger.info(msg=f'The Operational Log was Created or Re-created.')
            logger.debug(msg=f'Starting Ingestion')
            self.ingest_objects()
            logger.debug(msg=f'Completed Ingestion')
    
    def ingest_objects(self):
        try:
            logger.debug(msg=f'Ingest Objects')
            processed_file, created = ProcessedFile.objects.get_or_create(file_path=self.file_path)
            logger.info(msg=f'Processing File Created {created} {self.file_path}')
            with open(self.file_path, 'r') as file:
                file_size = os.fstat(file.fileno()).st_size
                logger.debug(msg=f'File Size {file_size} Last Processed Position {processed_file.last_processed_position}')
                if processed_file.last_processed_position > file_size:
                    processed_file.last_processed_position = 0

                file.seek(processed_file.last_processed_position)
                logger.debug(msg=f'Starting Reading Files')
                line = file.readline()
                while line:
                    ingest_object(line)
                    line = file.readline()
                logger.debug(msg=f'File Processed, now at locaiton {file.tell()}')
                processed_file.last_processed_position = file.tell()
                processed_file.save()
        except EOFError:
            pass
        except Exception as e:
            logger.error(msg=f'ingest_objects {e}')
            logger.error(msg=f'ingest_object ERROR {traceback.format_exc()}')

class Command(BaseCommand):
    help = 'Read serialized objects from a file and save them, watching for changes in the file.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the file to watch and ingest objects from.')

    def handle(self, *args, **options):
        file_path = options['file_path']
        handler = ObjectIngestHandler(file_path)
        handler.ingest_objects()
        observer = Observer()
        observer.schedule(handler, os.path.dirname(file_path), recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()