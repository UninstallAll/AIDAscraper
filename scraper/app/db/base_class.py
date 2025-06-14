"""
SQLAlchemy基类模块
"""
import re
from typing import Any, Dict

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    SQLAlchemy基类
    
    所有模型都应该继承这个类
    """
    id: Any
    __name__: str
    
    # 自动生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        """
        将类名转换为蛇形命名的表名
        
        例如: UserModel -> user_model
        """
        # 将驼峰命名转换为蛇形命名
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    def dict(self) -> Dict[str, Any]:
        """
        将模型转换为字典
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 