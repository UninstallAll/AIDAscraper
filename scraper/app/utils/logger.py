"""
爬虫任务日志记录器
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from app import models, schemas, services
from app.core.websocket_manager import manager
from app.db.database import SessionLocal


class JobLogger:
    """
    爬虫任务日志记录器
    """
    def __init__(self, job_id: int):
        self.job_id = job_id
        self.logger = logging.getLogger(f"job_{job_id}")
        self.logger.setLevel(logging.INFO)
    
    def _create_log_entry(
        self, 
        level: str, 
        message: str,
        db: Optional[Session] = None
    ) -> models.JobLog:
        """
        创建日志记录
        
        Args:
            level: 日志级别
            message: 日志消息
            db: 数据库会话，如果为None则创建新会话
            
        Returns:
            models.JobLog: 创建的日志记录
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        
        try:
            log_data = schemas.JobLogCreate(
                job_id=self.job_id,
                level=level,
                message=message,
                timestamp=datetime.now()
            )
            log = services.job_log.create(db, obj_in=log_data)
            return log
        finally:
            if close_db:
                db.close()
    
    async def _send_log_via_websocket(self, log_data: Dict[str, Any]) -> None:
        """
        通过WebSocket发送日志
        
        Args:
            log_data: 日志数据
        """
        await manager.send_log(self.job_id, log_data)
    
    def log(self, level: str, message: str, db: Optional[Session] = None) -> None:
        """
        记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
            db: 数据库会话
        """
        # 记录到标准日志
        if level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "DEBUG":
            self.logger.debug(message)
        
        # 保存到数据库
        log = self._create_log_entry(level, message, db)
        
        # 通过WebSocket发送
        log_data = {
            "id": log.id,
            "job_id": log.job_id,
            "level": log.level,
            "message": log.message,
            "timestamp": log.timestamp.isoformat()
        }
        
        # 使用异步事件循环发送WebSocket消息
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._send_log_via_websocket(log_data))
            else:
                loop.run_until_complete(self._send_log_via_websocket(log_data))
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            asyncio.run(self._send_log_via_websocket(log_data))
        except Exception as e:
            self.logger.error(f"发送WebSocket消息失败: {e}")
    
    def info(self, message: str, db: Optional[Session] = None) -> None:
        """记录INFO级别日志"""
        self.log("INFO", message, db)
    
    def warning(self, message: str, db: Optional[Session] = None) -> None:
        """记录WARNING级别日志"""
        self.log("WARNING", message, db)
    
    def error(self, message: str, db: Optional[Session] = None) -> None:
        """记录ERROR级别日志"""
        self.log("ERROR", message, db)
    
    def debug(self, message: str, db: Optional[Session] = None) -> None:
        """记录DEBUG级别日志"""
        self.log("DEBUG", message, db)


def get_job_logger(job_id: int) -> JobLogger:
    """
    获取任务日志记录器
    
    Args:
        job_id: 任务ID
        
    Returns:
        JobLogger: 任务日志记录器
    """
    return JobLogger(job_id) 