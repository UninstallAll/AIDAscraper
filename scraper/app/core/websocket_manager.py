"""
WebSocket连接管理器
"""
import json
import logging
from typing import Dict, List, Optional, Any

from fastapi import WebSocket

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket连接管理器
    """
    def __init__(self):
        # 所有活跃连接: {job_id: {client_id: websocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, job_id: int, client_id: str) -> None:
        """
        建立WebSocket连接
        
        Args:
            websocket: WebSocket连接
            job_id: 任务ID
            client_id: 客户端ID
        """
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = {}
        self.active_connections[job_id][client_id] = websocket
        logger.info(f"Client {client_id} connected to job {job_id}")
    
    def disconnect(self, job_id: int, client_id: str) -> None:
        """
        断开WebSocket连接
        
        Args:
            job_id: 任务ID
            client_id: 客户端ID
        """
        if job_id in self.active_connections and client_id in self.active_connections[job_id]:
            del self.active_connections[job_id][client_id]
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
            logger.info(f"Client {client_id} disconnected from job {job_id}")
    
    async def send_log(self, job_id: int, log_data: Dict[str, Any]) -> None:
        """
        发送日志消息给指定任务的所有连接
        
        Args:
            job_id: 任务ID
            log_data: 日志数据
        """
        if job_id not in self.active_connections:
            return
        
        disconnected = []
        for client_id, websocket in self.active_connections[job_id].items():
            try:
                await websocket.send_json(log_data)
            except Exception as e:
                logger.error(f"Error sending log to client {client_id}: {e}")
                disconnected.append((job_id, client_id))
        
        # 清理断开的连接
        for job_id, client_id in disconnected:
            self.disconnect(job_id, client_id)
    
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        向所有连接广播消息
        
        Args:
            message: 消息内容
        """
        disconnected = []
        for job_id in self.active_connections:
            for client_id, websocket in self.active_connections[job_id].items():
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to client {client_id}: {e}")
                    disconnected.append((job_id, client_id))
        
        # 清理断开的连接
        for job_id, client_id in disconnected:
            self.disconnect(job_id, client_id)
    
    def get_clients_count(self, job_id: Optional[int] = None) -> int:
        """
        获取连接的客户端数量
        
        Args:
            job_id: 任务ID，如果为None则返回所有连接数
            
        Returns:
            int: 客户端数量
        """
        if job_id is not None:
            return len(self.active_connections.get(job_id, {}))
        
        return sum(len(clients) for clients in self.active_connections.values())


# 创建全局WebSocket连接管理器实例
manager = ConnectionManager() 