// discord服务，请求discord第三方接口
import { config } from '@/config.js'
import { discordClient } from '@/services/axios-client.js'
import { Result } from '@/common.js'

class DiscordService {
  async fetchUserAvatar(userId, avatarHash) {
    const avatarURL = `${config['DISCORD_IMAGE_BASE_URL']}/avatars/${userId}/${avatarHash}.png`
    const response = await discordClient.get(avatarURL, { responseType: "blob" })
    return new Result(response.status, '', response.data)
  }
}

export const discordService = new DiscordService();
