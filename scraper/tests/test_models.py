"""
模型测试
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import User
from app.models.site import SiteConfig
from app.models.job import Job
from app.db.database import Base


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    # 使用内存数据库
    engine = create_engine("sqlite:///:memory:")
    # 创建表
    Base.metadata.create_all(engine)
    # 创建会话
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def test_user_model(db_session):
    """测试用户模型"""
    # 创建用户
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User",
        tenant_id="test_tenant",
        role="admin",
    )
    
    # 添加到数据库
    db_session.add(user)
    db_session.commit()
    
    # 查询用户
    db_user = db_session.query(User).filter(User.username == "testuser").first()
    
    # 验证
    assert db_user is not None
    assert db_user.email == "test@example.com"
    assert db_user.username == "testuser"
    assert db_user.hashed_password == "hashed_password"
    assert db_user.full_name == "Test User"
    assert db_user.tenant_id == "test_tenant"
    assert db_user.role == "admin"
    assert db_user.is_active is True
    assert db_user.is_superuser is False


def test_site_config_model(db_session):
    """测试站点配置模型"""
    # 创建站点配置
    site_config = SiteConfig(
        name="Test Site",
        url="https://example.com",
        description="Test Description",
        config={"key": "value"},
        tenant_id="test_tenant",
        start_urls=["https://example.com"],
        allowed_domains=["example.com"],
    )
    
    # 添加到数据库
    db_session.add(site_config)
    db_session.commit()
    
    # 查询站点配置
    db_site_config = db_session.query(SiteConfig).filter(SiteConfig.name == "Test Site").first()
    
    # 验证
    assert db_site_config is not None
    assert db_site_config.name == "Test Site"
    assert db_site_config.url == "https://example.com"
    assert db_site_config.description == "Test Description"
    assert db_site_config.config == {"key": "value"}
    assert db_site_config.tenant_id == "test_tenant"
    assert db_site_config.start_urls == ["https://example.com"]
    assert db_site_config.allowed_domains == ["example.com"]
    assert db_site_config.is_active is True


def test_job_model(db_session):
    """测试任务模型"""
    # 创建站点配置
    site_config = SiteConfig(
        name="Test Site",
        url="https://example.com",
        config={},
        tenant_id="test_tenant",
    )
    db_session.add(site_config)
    db_session.commit()
    
    # 创建用户
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        tenant_id="test_tenant",
    )
    db_session.add(user)
    db_session.commit()
    
    # 创建任务
    job = Job(
        name="Test Job",
        site_config_id=site_config.id,
        status="pending",
        progress=0,
        items_scraped=0,
        items_saved=0,
        tenant_id="test_tenant",
        created_by_id=user.id,
    )
    db_session.add(job)
    db_session.commit()
    
    # 查询任务
    db_job = db_session.query(Job).filter(Job.name == "Test Job").first()
    
    # 验证
    assert db_job is not None
    assert db_job.name == "Test Job"
    assert db_job.site_config_id == site_config.id
    assert db_job.status == "pending"
    assert db_job.progress == 0
    assert db_job.items_scraped == 0
    assert db_job.items_saved == 0
    assert db_job.tenant_id == "test_tenant"
    assert db_job.created_by_id == user.id 