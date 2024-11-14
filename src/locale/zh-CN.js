export default {
  'component': {
    'common-navbar': {
      'discord_logo': '🥳加入我们的Discord频道!',
      'github_logo': '🧐参与Musicatri的开发!',
      'setting_logo': '⚙️偏好设置'
    },
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
      'profile_setting': '账号'
    },
  },
  'view': {
    'AppearanceSetting': {
      'title': '外观设定',
      'language_setting': '语言设定',
      'language_setting_description': '您可以选择应用程序的显示语言。选择您熟悉的语言可以提高使用体验，让您更轻松地浏览内容和理解信息。',
      'language_select_label': '选择一种语言',
      'language_select_placeholder': '没有选择语言'
    },
    'ProfileSetting': {
      'title': '账号设定',
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
      'try_reconnect': '继续尝试重连',
      'sending_issue': '给开发者发送issue!',
      'current_retry_times': '正在进行第 {times} 次重连尝试',
      'error_occur_title': '连接状态异常',
      'retry_login': '返回重新登陆',
      'checking_login_status': '正在校验登录状态',
      'not_login_yet': '还没有登陆喵',
      'unknown_error': '未知异常',
      'server_error': '服务端异常',
      'client_error': '客户端异常',
    },
    'UserLoginCallback': {
      'return_login': '返回登录主页',
      'auth_success': '授权成功',
    }
  }
}
