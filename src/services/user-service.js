// 用户服务模块
import { store } from '@/storage/index.js'
import { musicatriClient } from '@/services/axios-client.js'
import { discordService } from '@/services/discord_service.js'
import { ToastMessage } from '@/utils/ui-helper.js'
import { Result } from '@/common.js'
import { i18n } from '@/locale/index.js'

const urlPrefix = '/users'
class UserService {
  // 获取当前用户详情信息
  getUserDetails(user_id=null) {
    if (user_id == null) {
      return musicatriClient.get(`${urlPrefix}/me/details`)
    }
  }

  loadUserDetails() {
    return new Promise(resolve => {
      userService.getUserDetails().then(async result => {
        if (result.code === 200) {
          // 成功拉取用户数据，将用户数据设置到vuex
          await store.dispatch('setCurrentUser', result.data)
        }
        resolve(result)
      })
    })
  }

  async loadUserAvatar() {
    if (store.getters.userAvatarStatus === 'loading') {
      return new Result(400, 'Avatar is loading')
    }
    // 非竞态action
    await store.dispatch('setUserAvatarStatus', 'loading')
    const user = store.getters.currentUser
    if (user.avatar === null) {
      await store.dispatch('setUserAvatarStatus', 'unset')
      return new Result(404, 'User info not found')
    }
    const result = await discordService.fetchUserAvatar(user.id, user.avatar)
    let avatarURL = null
    let avatarStatus = 'unset'
    if (result.isSuccess()) {  // 成功拉取用户头像信息
      avatarURL = URL.createObjectURL(result.data)
      avatarStatus = 'completed'
    } else {
      // 头像拉取失败
      ToastMessage.error(i18n.global.t('component.user-avatar.fetch_avatar_failed'))
    }
    await store.dispatch('setUserAvatarURL', avatarURL)
    await store.dispatch('setUserAvatarStatus', avatarStatus)
    return result
  }
}

export const userService = new UserService();
