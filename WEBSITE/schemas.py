from pydantic import BaseModel, Field


class ValuationRequest(BaseModel):
    location: str
    sublocality: str
    ptype: str
    furnish: str
    area: float = Field(ge=500, le=20000)
    bedrooms: int = Field(ge=1, le=8)
    bathrooms: int = Field(ge=1, le=6)
    stories: int = Field(ge=1, le=4)
    parking: int = Field(ge=0, le=4)
    age: float = Field(ge=0, le=45)
    mainroad: bool = True
    guestroom: bool = False
    basement: bool = False
    hotwater: bool = False
    ac: bool = True
    prefarea: bool = True


class ChatRequest(BaseModel):
    message: str
    valuation: dict  # the last /api/valuate response, sent back by the client so the
                      # server stays stateless between requests
