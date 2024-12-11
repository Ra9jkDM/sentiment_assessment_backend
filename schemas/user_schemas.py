from pydantic import BaseModel, Field, EmailStr

class UserLoginModel(BaseModel):
    username: EmailStr
    password: str = Field(min_length=8, max_length=100)
    
class UserSchema(BaseModel):
    username: EmailStr
    firstname: str = Field(min_length=2, max_length=100)
    lastname: str | None
    is_active: bool
    
class UserRegistrationSchema(UserLoginModel, UserSchema):
    pass


class UserDTO(UserRegistrationSchema):
    salt: str | None = ''