from typing import Type, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import tool, BaseTool
from ultralytics import YOLO
import json


class Tool_helmet_input(BaseModel):
    """Input schema for MyCustomTool."""

    argument: Dict[str, Any]= Field(..., description="location file")


class Tool_helmet(BaseTool):
    name: str = "tool_deteksi_helmet"
    description: str = "tool latihan untuk deteksi helmet"
    args_schema: Type[BaseModel] = Tool_helmet_input

    modelVision: YOLO = YOLO("src/pelatihanindoprima/tools/model_yolo.pt")    

    def _run(self, argument: str) -> str:
        # Implementation goes here
        hasilDeteksi = self.modelVision(argument)
        detected_object = hasilDeteksi[0].boxes.cls.tolist()
        class_names = hasilDeteksi[0].names
        object_count = {}
        head=0
        helmet=0
        person=0
        for hasil in detected_object:
            nama_class = class_names[int(hasil)]
            if (nama_class == "head"):
                head = head + 1
            elif (nama_class == "helmet"):
                helmet = helmet + 1
            else:
                person = person + 1

        result_dict = {
            "result": f"Detected {person} person(s), {helmet} helmet(s), {head} head(s) without helmet",
            "head": head,
            "person": person,
            "helmet": helmet
        }

        return str(result_dict)
        # return "this is an example of a tool output, ignore it and move along."
