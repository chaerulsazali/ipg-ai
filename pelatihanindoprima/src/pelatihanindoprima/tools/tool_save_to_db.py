from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import tool, BaseTool
import mysql.connector
from typing import Optional

class Tool_save_to_db_input(BaseTool):
    head: int = Field(..., description="count of head detected")
    person: int = Field(..., description="count of person detected")
    helmet: int = Field(..., description="count of helmet detected")

class Tool_save_to_db(BaseTool):
    name: str = "tools report ke db"
    description: str = "Store detection results to database for record keeping"
    args_schema: Type[BaseModel] = Tool_save_to_db_input
    
    def _run(self, head:int, person:int, helmet:int) -> str:
        try:
            connec = mysql.connector.connect(
                host = "127.0.0.1",
                user = "root",
                password = "root",
                database = "indoprima"
            )
            cursor = connec.cursor()
            if (head > 0):
                detil = "{head} heads, {helmet} helmets, and {person} persons"
                query = "INSERT INTO helmet_report (report_result,report_detected) VALUES (%s, %s)"
                cursor.execute(query, (detil, head))
                connec.commit()

                cursor.close()
                connec.close()
                return ("stored to db")
            else:
                return ("report that everbody is safe")
            
            return str("total of head is {head}")
        except Exception as e:
            raise(Exception(e))