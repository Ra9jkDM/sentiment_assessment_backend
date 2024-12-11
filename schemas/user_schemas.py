from pydantic import BaseModel, Field, EmailStr

class UserLoginModel(BaseModel):
    username: EmailStr
    password: str = Field(min_length=8, max_length=100)
    is_active: bool = True
    
class UserSchema(BaseModel):
    username: EmailStr
    firstname: str = Field(min_length=2, max_length=100)
    lastname: str | None
    
class UserRegistrationSchema(UserLoginModel, UserSchema):
    pass


class UserDTO(UserRegistrationSchema):
    salt: str | None = ''