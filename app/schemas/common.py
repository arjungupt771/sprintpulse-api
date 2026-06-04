from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DateRangeModel(ApiModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_date_order(self) -> "DateRangeModel":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class NonEmptyStringMixin(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def validate_non_empty_strings(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            raise ValueError("field cannot be empty")
        return value

