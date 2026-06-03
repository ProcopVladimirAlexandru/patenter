from patenter.models.patents import PatentDatesModel, PatentClaimModel, PatentModel


class PatentDatesRequestModel(PatentDatesModel):
    pass


class PatentClaimRequestModel(PatentClaimModel):
    pass


class PatentRequestModel(PatentModel):
    pass

    def to_internal_model(self) -> PatentModel:
        return PatentModel(**self.model_dump())
