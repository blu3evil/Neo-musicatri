export default {
  'el': {
    'pagination': {
      'goto': '前往',
      'pageClassifier': '页',
    }
  },
  'global': {
    'admin': '管理员',
    'user': '用户',
    'traveler': '游客',
    'active': '已激活',
    'banned': '被禁用',
    'any': '任意',
  },
  'component': {
    'common-navbar': {},
    'pending-panel': {
      'footer': '版权所有© 2072 株式会社山崎制造',
      'client_error': '客户端异常',
      'server_error': '服务端异常',
      'response_success': '服务端响应成功',
      'login_page_link': '返回认证主页',
      'waiting_response': '等待后端响应',
      'auth_code_not_exists': '没有找到授权码',
      'issue_page_link': '发送issue！',
      'unknown_error': '未知异常',
      'authenticate_success': '授权成功',
      'authenticate_failed': '授权失败',
    },
    'redirect-panel': {
      'footer': '版权所有© 2072 株式会社山崎制造',
      'to_discord': '点这里前往discord授权喵',
      'title': '还没有登录喵~'
    },
    'setting-sidebar': {
      'appearance_setting': '外观',
      'profile_setting': '账号',
      'about_setting': '关于',
      'atri_setting': '亚托莉设定'
    },
    'user-panel': {
      'more_settings': '应用设置',
      'account_logout': '账户登出',
      'confirm_logout': '真的要退出嘛？',
    },
    'user-avatar': {
      'fetch_avatar_failed': '获取用户头像失败',
    },
    'loading-string': {
      'on-loading': '加载中'
    },
    'atri-status-panel': {
      'atri_stopped': '未运行',
      'atri_started': '运行中',
      'atri_starting': '启动中',
      'atri_stopping': '停止中',
      'atri_failed': '状态异常',
    }
  },
  'view': {
    'workspace': {
      'Workspace': {
        'portal': '指南针',
        'quick_start': '快速开始',
        'admin_function': '管理员功能',
        'app-management': '应用面板',
        'user_management': '用户面板',
        'musiclib_management': '曲库面板',
        'bot_management': '机器人',
      },
      'Portal': {},
      'Dashboard': {
        'overview': '应用总览',
        'log_monitoring': '日志监控',
      },
      'UserManagement': {
        'overview': '用户总览',
        'management': '用户管理',
        'username_label': '标识名',
        'global_name_label': '用户名',
        'user_id': '用户id',
        'roles_label': '权限',
        'is_active_label': '状态',
        'query': '检索',
        'fuzzy_query_placeholder': "使用'*'进行模糊匹配",
        'empty_text': '亚托莉什么也没有找到>.<',
        'submit_change_or_not': '要提交此次修改嘛?',
        'submit_change_success': '成功修改{globalName}用户的数据',
        'operation_label': '操作',
        'delete_user': '删除用户',
        'delete_user_or_not': '真的要删除用户{globalName}的数据嘛',
        'delete_user_failed': '用户{globalName}删除失败: {reason}',
        'delete_user_success': '用户{globalName}删除成功'
      },
      'MusiclibManagement': {
        'overview': '曲库总览',
        'management': '曲库管理',
      },
      'BotManagement': {
        'overview': '机器人总览',
      }
    },
    'AppearanceSetting': {
      'title': '外观设定',
      'language_setting': '语言设定',
      'language_setting_description': '您可以选择应用程序的显示语言。选择您熟悉的语言可以提高使用体验，让您更轻松地浏览内容和理解信息。',
      'language_select_label': '选择一种语言',
      'language_select_placeholder': '没有选择语言',
      'theme_setting': '主题设定',
      'theme_select_label': '选择偏好主题',
      'theme_select_placeholder': '没有选择主题'
    },
    'ProfileSetting': {
      'title': '账号信息',
    },
    'AboutSetting': {
      'title': '关于音乐亚托莉',
      'musicatri_audio1': '"是吧，我是高性能的嘛，哼哼!"',
      'musicatri_audio2': '"好吃就是高兴嘛!"',
      'musicatri_audio3': '"地球也包括我吗?"',
      'system_info': '服务端信息',
      'system_name': '名称',
      'system_version': '版本',
      'system_description': '描述',
      'dashboard_connection': '管理员',
      'connect_dashboard': '提权',
      'disconnect_dashboard': '降权',
      'button_disable': '不可用',
      'connected': '已提权',
      'connecting': '提权中',
      'disconnecting': '降权中',
      'disconnected': '未提权',
      'discord_logo': '我们的Discord频道',
      'github_logo': '项目源代码',
      'admin_function': '管理员功能',
      'admin_function_enable_success': '管理员功能开启',
      'admin_function_enable_failed': '管理员功能开启失败: {reason}',
      'admin_function_disable_success': '管理员功能关闭',
      'admin_function_disable_failed': '管理员功能关闭失败: {reason}'
    },
    'UserLoginPending': {
      'invalid_auth_code': '非法的认证code参数'
    },
    'UserLogin': {
      'checking_musicatri_status': '检查亚托莉状态中',

      'fixing_musicatri': '无法连接到亚托莉',
      'expired_credential': '登录凭证过期，需要重新认证',

      'retry_auth_code': '重新授权discord',
      'authenticate_success': '认证成功',
      'authenticate_fail': '认证失败',

      'to_discord': '点这里前往discord授权喵',
      'connect_exception': '连接异常',

      'reach_reconnect_limit': '无法建立到服务端的连接',
      'reach_reconnect_limit_subtitle': '重连次数达到上线',
      'try_reconnect': '尝试重连',
      'sending_issue': '发送issue!',
      'current_retry_times': '正在进行第 {times} 次重连尝试',
      'error_occur_title': '连接状态异常',
      'connection_error': '连接状态异常',
      'retry_login': '返回重新登陆',
      'retry_connect': '尝试重新连接',
      'checking_login_status': '正在校验登录状态',
      'not_login_yet': '还没有登陆喵',
      'unknown_error': '未知异常',
      'server_error': '服务端异常',
      'client_error': '客户端异常',
      'load_user_details': '加载用户数据'
    },
    'UserLoginCallback': {
      'retry_authorize': '重新授权',
      'return_login': '返回主页',
      'auth_success': '授权成功',
      'awaiting_authorize': '等待跳转',
      'user_login': '登录中',
    },
    'NotFound': {
      'title': '这个路径不存在(っ`-´c)!',
      'return_index': '返回主页',
    }
  },
  'services': {
    'auth-service': {
      'login_status_expired_confirm': '返回主页',
      'login_status_expired_title': '登录状态过期',
      'login_status_expired_message': '过期的登录状态会自动中断您的长连接，请返回主页重新登录...'
    },
  },
  'sockets': {
    'socket-context': {
      'timeout': '等待超时',
    },
    'admin-socket': {
      'disconnect_failed': '管理员连接断开失败: {reason}',
      'connect_failed': '管理员功能连接失败: {reason}',
      'connect_success': '管理员功能开启',
      'disconnect_success': '管理员功能关闭',
      'connect_shutdown': '管理员连接被神秘力量中断了...',
      'disconnect_timeout': '管理员连接断开失败，等待超时',
      'atri_state_change': '亚托莉状态变更: {identify}'
    },
    'user-socket': {
      'disconnect_failed': '用户连接断开失败: {reason}',
      'connect_shutdown': '用户长连接被神秘力量中断了...',
      'disconnect_timeout': '用户连接断开失败，等待超时',
    }
  },
  'utils': {
    'ui-helper': {
      'toast_message_error_title': '有些事情不对劲!',
      'toast_message_success_title': '执行成功',
      'toast_message_warning_title': '严重警告',
      'toast_message_info_title': '提示',
      'popup_message_warning_title': '这是一条警告',
      'popup_message_warning_confirm': '确定',
      'popup_message_warning_cancel': '取消',
      'system_info_load_failed': '服务器信息获取失败',
    }
  }
}
