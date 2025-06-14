"""
系统维护任务模块
"""
import logging
import os
from datetime import datetime, timedelta

from app.core.celery_app import celery_app
from app.db.database import SessionLocal

# 设置日志
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=2)
def daily_maintenance(self) -> dict:
    """
    每日维护任务
    
    Returns:
        dict: 任务执行结果
    """
    logger.info("开始执行每日维护任务")
    
    results = {
        "log_cleanup": False,
        "temp_cleanup": False,
    }
    
    try:
        # 清理过期日志
        results["log_cleanup"] = cleanup_old_logs()
        
        # 清理临时文件
        results["temp_cleanup"] = cleanup_temp_files()
        
        logger.info("每日维护任务执行完成")
        return {"status": "success", "results": results}
    except Exception as e:
        logger.exception(f"每日维护任务失败: {e}")
        raise self.retry(exc=e, countdown=300)


def cleanup_old_logs(days: int = 7) -> bool:
    """
    清理过期日志
    
    Args:
        days: 保留天数
        
    Returns:
        bool: 是否成功
    """
    try:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            return True
        
        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=days)
        count = 0
        
        # 遍历日志目录
        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            
            # 检查是否是文件
            if os.path.isfile(file_path):
                # 获取文件修改时间
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # 如果文件过期，则删除
                if file_time < cutoff_date:
                    os.remove(file_path)
                    count += 1
        
        logger.info(f"清理了 {count} 个过期日志文件")
        return True
    except Exception as e:
        logger.exception(f"清理过期日志失败: {e}")
        return False


def cleanup_temp_files() -> bool:
    """
    清理临时文件
    
    Returns:
        bool: 是否成功
    """
    try:
        temp_dir = "tmp"
        if not os.path.exists(temp_dir):
            return True
        
        # 计算截止日期（1天前）
        cutoff_date = datetime.now() - timedelta(days=1)
        count = 0
        
        # 遍历临时目录
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            
            # 检查是否是文件
            if os.path.isfile(file_path):
                # 获取文件修改时间
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # 如果文件过期，则删除
                if file_time < cutoff_date:
                    os.remove(file_path)
                    count += 1
        
        logger.info(f"清理了 {count} 个临时文件")
        return True
    except Exception as e:
        logger.exception(f"清理临时文件失败: {e}")
        return False 