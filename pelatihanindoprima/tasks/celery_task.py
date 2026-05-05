from tasks.celery_app import celery_app
from src.pelatihanindoprima.crews.content_crew.content_crew import ContentCrew
from src.pelatihanindoprima.crews.it_support.it_support import ItSupport
from src.pelatihanindoprima.crews.analisator.analisator import Analisator
from src.pelatihanindoprima.crews.file_anlyzer.file_anlyzer import FileAnlyzer
import logging
import traceback

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="research")
def research(self, topic:str):
    self.update_state(state='RUNNING', meta={'current':f'start job for{topic}'})
    try:
        result = ContentCrew().crew().kickoff(inputs={"topic":topic})
        return str(result)
    except Exception as e:
        logger.error(f"Task failed with error: {e}\n{traceback.format_exc()}")
        raise

@celery_app.task(bind=True, name="it_support")
def it_support(self, issue_description:str, priority_level:str):
    self.update_state(state='RUNNING', meta={'current':f'start job for{issue_description,priority_level}'})
    try:
        result = ItSupport().crew().kickoff(inputs={"issue_description":issue_description,"priority_level":priority_level})
        return str(result)
    except Exception as e:
        logger.error(f"Task failed with error: {e}\n{traceback.format_exc()}")
        raise

@celery_app.task(bind=True, name="analisator")
def analisator(self, topic:str):
    self.update_state(state='RUNNING', meta={'current':f'start job for{topic}'})
    try:
        result = Analisator().crew().kickoff(inputs={"topic":topic})
        return str(result)
    except Exception as e:
        logger.error(f"Task failed with error: {e}\n{traceback.format_exc()}")
        raise

@celery_app.task(bind=True, name="file_txt_analyzer")
def file_txt_analyzer(self, file:str):
    self.update_state(state='RUNNING', meta={'current':f'start job for{file}'})
    try:
        result = FileAnlyzer().crew().kickoff(inputs={"file":file})
        return result.raw
    except Exception as e:
        logger.error(f"Task failed with error: {e}\n{traceback.format_exc()}") 