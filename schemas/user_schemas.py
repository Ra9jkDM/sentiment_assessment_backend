from pydantic import BaseModel, Field, EmailStr

class UserPassword(BaseModel):
    password: str = Field(min_length=8, max_length=100)

class UserLoginModel(UserPassword):
    username: EmailStr
    is_active: bool = True
    
class UserSchema(BaseModel):
    username: EmailStr
    firstname: str = Field(min_length=2, max_length=100)
    lastname: str | None
    
class UserRegistrationSchema(UserLoginModel, UserSchema):
    pass

class UserDTO(UserRegistrationSchema):
    salt: str | None = ''