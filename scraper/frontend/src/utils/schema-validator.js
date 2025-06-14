/**
 * JSON Schema验证器
 * 用于验证站点配置是否符合JSON Schema规范
 */

// 站点配置的JSON Schema
const siteConfigSchema = {
  type: 'object',
  required: ['name', 'url', 'start_urls'],
  properties: {
    name: {
      type: 'string',
      title: '站点名称',
      description: '爬虫站点的名称'
    },
    url: {
      type: 'string',
      format: 'uri',
      title: '站点URL',
      description: '爬虫站点的主URL'
    },
    description: {
      type: 'string',
      title: '站点描述',
      description: '爬虫站点的描述信息'
    },
    requires_login: {
      type: 'boolean',
      title: '需要登录',
      description: '站点是否需要登录才能访问'
    },
    login_url: {
      type: 'string',
      format: 'uri',
      title: '登录页面URL',
      description: '站点登录页面的URL'
    },
    login_username_field: {
      type: 'string',
      title: '用户名字段名',
      description: '登录表单中用户名字段的名称'
    },
    login_password_field: {
      type: 'string',
      title: '密码字段名',
      description: '登录表单中密码字段的名称'
    },
    login_username: {
      type: 'string',
      title: '用户名',
      description: '登录用户名'
    },
    login_password: {
      type: 'string',
      title: '密码',
      description: '登录密码'
    },
    start_urls: {
      type: 'array',
      title: '起始URL列表',
      description: '爬虫开始爬取的URL列表',
      items: {
        type: 'string',
        format: 'uri'
      }
    },
    allowed_domains: {
      type: 'array',
      title: '允许的域名',
      description: '爬虫允许爬取的域名列表',
      items: {
        type: 'string'
      }
    },
    list_page_xpath: {
      type: 'string',
      title: '列表页XPath',
      description: '用于提取列表页中项目的XPath表达式'
    },
    next_page_xpath: {
      type: 'string',
      title: '下一页XPath',
      description: '用于提取下一页链接的XPath表达式'
    },
    detail_page_xpath: {
      type: 'string',
      title: '详情页XPath',
      description: '用于提取详情页内容的XPath表达式'
    },
    field_mappings: {
      type: 'object',
      title: '字段映射',
      description: '字段名到XPath表达式的映射',
      additionalProperties: {
        type: 'string'
      }
    },
    use_playwright: {
      type: 'boolean',
      title: '使用Playwright',
      description: '是否使用Playwright渲染JavaScript'
    },
    config: {
      type: 'object',
      title: '爬虫配置',
      description: '爬虫的额外配置参数',
      additionalProperties: true
    },
    is_active: {
      type: 'boolean',
      title: '是否激活',
      description: '站点配置是否处于激活状态'
    },
    tenant_id: {
      type: 'string',
      title: '租户ID',
      description: '站点配置所属的租户ID'
    }
  }
}

/**
 * 验证站点配置是否符合JSON Schema
 * @param {Object} config - 站点配置对象
 * @returns {Object} - 验证结果，包含是否有效和错误信息
 */
export function validateSiteConfig(config) {
  // 这里简单实现一些基本验证
  const errors = []
  
  // 检查必填字段
  if (!config.name) {
    errors.push('站点名称不能为空')
  }
  
  if (!config.url) {
    errors.push('站点URL不能为空')
  } else if (!isValidUrl(config.url)) {
    errors.push('站点URL格式不正确')
  }
  
  if (!config.start_urls || config.start_urls.length === 0) {
    errors.push('起始URL列表不能为空')
  } else {
    for (const url of config.start_urls) {
      if (!isValidUrl(url)) {
        errors.push(`起始URL "${url}" 格式不正确`)
        break
      }
    }
  }
  
  // 如果需要登录，检查登录相关字段
  if (config.requires_login) {
    if (!config.login_url) {
      errors.push('登录页面URL不能为空')
    } else if (!isValidUrl(config.login_url)) {
      errors.push('登录页面URL格式不正确')
    }
    
    if (!config.login_username_field) {
      errors.push('用户名字段名不能为空')
    }
    
    if (!config.login_password_field) {
      errors.push('密码字段名不能为空')
    }
    
    if (!config.login_username) {
      errors.push('用户名不能为空')
    }
    
    if (!config.login_password) {
      errors.push('密码不能为空')
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * 检查URL是否有效
 * @param {string} url - 要检查的URL
 * @returns {boolean} - URL是否有效
 */
function isValidUrl(url) {
  try {
    new URL(url)
    return true
  } catch (e) {
    return false
  }
}

/**
 * 获取站点配置的JSON Schema
 * @returns {Object} - 站点配置的JSON Schema
 */
export function getSiteConfigSchema() {
  return siteConfigSchema
}

export default {
  validateSiteConfig,
  getSiteConfigSchema
} 