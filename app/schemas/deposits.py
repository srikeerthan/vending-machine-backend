import json

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Deposits(BaseModel):
    coins: list[dict] = Field(default_factory=list,
                              title="List of dicts containing coins value as key and quantity as value",
                              json_schema_extra={"example": [{"value": 5, "quantity": 10}, {"value": 10, "quantity": 5},
                                                             {"value": 20, "quantity": 3}, {"value": 50, "quantity": 2},
                                                             {"value": 100, "quantity": 1}]}
                              )

    @field_validator('coins', mode='before')
    def convert_roles_to_list(cls, v) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v


class DepositInCreate(Deposits):
    ...


class DepositInUpdate(Deposits):
    ...


class DepositsInDB(Deposits):
    model_config = ConfigDict(from_attributes=True)
